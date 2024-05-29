#!/usr/bin/env python3

from moviepy.editor import VideoFileClip, CompositeVideoClip
import subprocess
import tempfile
import whisper
import json
import sys
import os

from text_drawer import get_text_size, create_text
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
font_color = "#35dc0a"
padding = 50
position = ("center", "center")

def fits_frame(frame_width):
    def fit_function(text):
        return len(calculate_lines(text, frame_width)["lines"]) <= 1
    return fit_function

def calculate_lines(text, frame_width):
    lines_to_write = []

    line_to_draw = None
    line = ""
    words = text.split()
    word_index = 0
    while word_index < len(words):
        word = words[word_index]
        line += word + " "
        text_size = get_text_size(line.strip(), font_size, font, stroke_width)
        text_width = text_size[0]
        line_height = text_size[1]

        if text_width > frame_width:
            if line_to_draw:
                lines_to_write.append(line_to_draw)
                line_to_draw = None
            line = ""
        else:
            line_to_draw = line.strip()
            word_index += 1

    if line_to_draw:
        lines_to_write.append(line_to_draw)

    return {
        "lines": lines_to_write,
        "height": line_height,
    }

def ffmpeg(command):
    return subprocess.run(command, capture_output=True)

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
        line_data = calculate_lines(caption["text"], text_bbox_width)

        lines = "\n".join(line_data["lines"])

        text = create_text(lines, font_size, font_color, font, stroke_color=stroke_color, stroke_width=stroke_width)
        text = text.set_start(caption["start"])
        text = text.set_duration(caption["end"] - caption["start"])
        text = text.set_position(position)

        clips.append(text)

    video_with_text = CompositeVideoClip(clips)

    video_with_text.write_videofile(output_file, codec="libx264", fps=video.fps)

if __name__ == "__main__":
    main()
