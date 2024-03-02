#!/usr/bin/env python3

import subprocess
import tempfile
import whisper
import math
import json
import sys
import cv2
import os

import segment_parser

video_file = sys.argv[1]
caption_y_pos = 0.5

current_dir = os.path.dirname(os.path.realpath(__file__))
output_file = os.path.join(current_dir, "with_transcript.avi")
temp_video_file = tempfile.NamedTemporaryFile(suffix=".avi").name
temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav").name

# TODO: make these parameters
font = cv2.FONT_HERSHEY_SIMPLEX
white_color = (255, 255, 255)
black_color = (0, 0, 0)
border = 5
margin = 18
thickness = 10
font_scale = 3

def fits_frame(frame_width):
    def fit_function(text):
        return len(calculate_lines(text, frame_width)["lines"]) <= 2
    return fit_function

def write_line(text, frame, text_y, font, font_scale, white_color, black_color, thickness, border):
    # Calculate the position for centered text
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (frame.shape[1] - text_size[0]) // 2  # Center horizontally
    org = (text_x, text_y)  # Position of the text

    frame = cv2.putText(frame, text, org, font, font_scale, black_color, thickness + border * 2, cv2.LINE_AA)
    frame = cv2.putText(frame, text, org, font, font_scale, white_color, thickness, cv2.LINE_AA)

    return frame

def calculate_lines(text, frame_width):
    lines_to_write = []

    line_to_draw = None
    line = ""
    words = text.split()
    word_index = 0
    while word_index < len(words):
        word = words[word_index]
        line += word + " "
        text_size = cv2.getTextSize(line.strip(), font, font_scale, thickness)[0]
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
    )

    segments = transcription["segments"]

    # Open the video file
    cap = cv2.VideoCapture(video_file)
    framerate = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    captions = segment_parser.parse(segments, fits_frame(frame_width))

    # Define the codec and create a VideoWriter object to save the output video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(temp_video_file, fourcc, framerate, (frame_width, frame_height))

    time = 0.0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        for caption in captions:
            if caption["start"] <= time and caption["end"] > time:
                line_data = calculate_lines(caption["text"], frame_width)
                line_height = int(line_data["height"] + margin)
                text_y = int(frame_height * caption_y_pos - (len(line_data["lines"]) * line_height / 2))
                for line in line_data["lines"]:
                    frame = write_line(line, frame, text_y, font, font_scale, white_color, black_color, thickness, border)
                    text_y += line_height
                break

        out.write(frame)

        time += 1/framerate

    # Release the VideoCapture and VideoWriter objects
    cap.release()
    out.release()

    # Close all OpenCV windows (if any)
    cv2.destroyAllWindows()

    ffmpeg([
        'ffmpeg',
        '-y',
        '-i', temp_video_file,
        '-i', temp_audio_file,
        '-map', '0:v',   # Map video from the first input
        '-map', '1:a',   # Map audio from the second input
        '-c:v', 'copy',  # Copy video codec
        '-c:a', 'aac',   # AAC audio codec
        '-strict', 'experimental',
        output_file
    ])

if __name__ == "__main__":
    main()
