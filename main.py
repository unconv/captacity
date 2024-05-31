#!/usr/bin/env python3

from moviepy.editor import VideoFileClip, CompositeVideoClip
import subprocess
import tempfile
import whisper
import json
import sys
import os

from text_drawer import get_text_size_ex, create_text_ex, blur_text_clip, Word
import segment_parser

video_file = sys.argv[1]

current_dir = os.path.dirname(os.path.realpath(__file__))
output_file = os.path.join(current_dir, "with_transcript.avi")
temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav").name

# TODO: make these parameters
font = "fonts/Bangers-Regular.ttf"
stroke_width = 3
stroke_color = "black"
font_size = 130
font_color = "yellow"
word_highlight_color = "red"
highlight_current_word = True
padding = 50
position = ("center", "center")
shadow_strength = 1.0
shadow_blur = 0.1

def fits_frame(frame_width):
    def fit_function(text):
        return len(calculate_lines(text, frame_width)["lines"]) <= 2
    return fit_function

def calculate_lines(text, frame_width):
    lines = []

    line_to_draw = None
    line = ""
    words = text.split()
    word_index = 0
    total_height = 0
    while word_index < len(words):
        word = words[word_index]
        line += word + " "
        text_size = get_text_size_ex(line.strip(), font_size, font, stroke_width)
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

def main():
    # Extract audio from video
    ffmpeg([
        'ffmpeg',
        '-y',
        '-i', video_file,
        temp_audio_file
    ])

    model = whisper.load_model("base")

    transcription = model.transcribe(
        audio=temp_audio_file,
        word_timestamps=True,
        fp16=False,
        initial_prompt=None,
    )

    segments = transcription["segments"]

    # Open the video file
    video = VideoFileClip(video_file)
    text_bbox_width = video.w-padding*2
    clips = [video]

    captions = segment_parser.parse(segments, fits_frame(text_bbox_width))

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
            line_data = calculate_lines(caption["text"], text_bbox_width)

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

    video_with_text = CompositeVideoClip(clips)

    video_with_text.write_videofile(output_file, codec="libx264", fps=video.fps)

if __name__ == "__main__":
    main()
