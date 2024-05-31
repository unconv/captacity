from moviepy.editor import VideoFileClip, CompositeVideoClip
import subprocess
import tempfile
import whisper
import time
import os

from . import segment_parser
from .text_drawer import (
    get_text_size_ex,
    create_text_ex,
    blur_text_clip,
    Word,
)

def fits_frame(line_count, font, font_size, stroke_width, frame_width):
    def fit_function(text):
        lines = calculate_lines(
            text,
            font,
            font_size,
            stroke_width,
            frame_width
        )
        return len(lines["lines"]) <= line_count
    return fit_function

def calculate_lines(text, font, font_size, stroke_width, frame_width):
    lines = []

    line_to_draw = None
    line = ""
    words = text.split()
    word_index = 0
    total_height = 0
    while word_index < len(words):
        word = words[word_index]
        line += word + " "
        text_size = get_text_size_ex(line.strip(), font, font_size, stroke_width)
        text_width = text_size[0]
        line_height = text_size[1]

        if text_width > frame_width:
            if line_to_draw:
                lines.append(line_to_draw)
                total_height += line_height
                line_to_draw = None
            line = ""
        else:
            line_to_draw = {
                "text": line.strip(),
                "height": line_height,
            }
            word_index += 1

    if line_to_draw:
        lines.append(line_to_draw)
        total_height += line_height

    return {
        "lines": lines,
        "height": total_height,
    }

def ffmpeg(command):
    return subprocess.run(command, capture_output=True)

def create_shadow(text, font_size, font, caption, position, blur_radius: float, opacity=1):
    shadow = create_text_ex(text, font_size, "black", font, opacity=opacity)

    shadow = blur_text_clip(shadow, int(font_size*blur_radius))

    shadow = shadow.set_start(caption["start"])
    shadow = shadow.set_duration(caption["end"] - caption["start"])
    shadow = shadow.set_position(position)

    return shadow

def get_font_path(font):
    if os.path.exists(font):
        return font

    dirname = os.path.dirname(__file__)
    font = os.path.join(dirname, "assets", "fonts", font)

    if not os.path.exists(font):
        raise FileNotFoundError(f"Font '{font}' not found")

    return font

def add_captions(
    video_file,
    output_file = "with_transcript.mp4",

    font = "Bangers-Regular.ttf",
    font_size = 130,
    font_color = "yellow",

    stroke_width = 3,
    stroke_color = "black",

    highlight_current_word = True,
    word_highlight_color = "red",

    line_count = 2,
    fit_function = None,

    padding = 50,
    position = ("center", "center"), # TODO: Implement this

    shadow_strength = 1.0,
    shadow_blur = 0.1,

    print_info = False,
):
    _start_time = time.time()

    font = get_font_path(font)

    if print_info:
        print("Extracting audio...")

    temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav").name
    ffmpeg([
        'ffmpeg',
        '-y',
        '-i', video_file,
        temp_audio_file
    ])

    if print_info:
        print("Transcribing audio...")

    model = whisper.load_model("base")

    transcription = model.transcribe(
        audio=temp_audio_file,
        word_timestamps=True,
        fp16=False,
        initial_prompt=None,
    )

    segments = transcription["segments"]

    if print_info:
        print("Generating video elements...")

    # Open the video file
    video = VideoFileClip(video_file)
    text_bbox_width = video.w-padding*2
    clips = [video]

    captions = segment_parser.parse(
        segments=segments,
        fit_function=fit_function if fit_function else fits_frame(
            line_count,
            font,
            font_size,
            stroke_width,
            text_bbox_width,
        ),
    )

    for caption in captions:
        captions_to_draw = []
        if highlight_current_word:
            for i, word in enumerate(caption["words"]):
                if i+1 < len(caption["words"]):
                    end = caption["words"][i+1]["start"]
                else:
                    end = word["end"]

                captions_to_draw.append({
                    "text": caption["text"],
                    "start": word["start"],
                    "end": end,
                })
        else:
            captions_to_draw.append(caption)

        for current_index, caption in enumerate(captions_to_draw):
            line_data = calculate_lines(caption["text"], font, font_size, stroke_width, text_bbox_width)

            text_y_offset = video.h // 2 - line_data["height"] // 2
            index = 0
            for line in line_data["lines"]:
                pos = ("center", text_y_offset)

                words = line["text"].split()
                word_list = []
                for w in words:
                    word_obj = Word(w)
                    if highlight_current_word and index == current_index:
                        word_obj.set_color(word_highlight_color)
                    index += 1
                    word_list.append(word_obj)

                # Create shadow
                shadow_left = shadow_strength
                while shadow_left >= 1:
                    shadow_left -= 1
                    shadow = create_shadow(word_list, font_size, font, caption, pos, shadow_blur, opacity=1)
                    clips.append(shadow)

                if shadow_left > 0:
                    shadow = create_shadow(word_list, font_size, font, caption, pos, shadow_blur, opacity=shadow_left)
                    clips.append(shadow)

                # Create text
                text = create_text_ex(word_list, font_size, font_color, font, stroke_color=stroke_color, stroke_width=stroke_width)
                text = text.set_start(caption["start"])
                text = text.set_duration(caption["end"] - caption["start"])
                text = text.set_position(pos)
                clips.append(text)

                text_y_offset += line["height"]

    if print_info:
        print("Rendering video...")

    video_with_text = CompositeVideoClip(clips)

    video_with_text.write_videofile(
        filename=output_file,
        codec="libx264",
        fps=video.fps,
        logger="bar" if print_info else None,
    )

    end_time = time.time()
    total_time = end_time - _start_time

    if print_info:
        print(f"Done in {total_time//60:02.0f}:{total_time%60:02.0f}")
