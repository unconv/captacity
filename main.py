import subprocess
import tempfile
import whisper
import json
import sys
import cv2
import os

video_file = sys.argv[1]

current_dir = os.path.dirname(os.path.realpath(__file__))
output_file = os.path.join(current_dir, "with_transcript.avi")
temp_video_file = tempfile.NamedTemporaryFile(suffix=".avi").name
temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav").name

def write_text(text, frame, video_writer):
    font = cv2.FONT_HERSHEY_SIMPLEX
    white_color = (255, 255, 255)
    black_color = (0, 0, 0)
    thickness = 10
    font_scale = 3
    border = 5

    # Calculate the position for centered text
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_x = (frame.shape[1] - text_size[0]) // 2  # Center horizontally
    text_y = (frame.shape[0] + text_size[1]) // 2  # Center vertically
    org = (text_x, text_y)  # Position of the text

    frame = cv2.putText(frame, text, org, font, font_scale, black_color, thickness + border * 2, cv2.LINE_AA)
    frame = cv2.putText(frame, text, org, font, font_scale, white_color, thickness, cv2.LINE_AA)

    video_writer.write(frame)

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

    words = {}

    for segment in segments:
        for word in segment["words"]:
            words[word["start"]] = word["word"]

    # Open the video file
    cap = cv2.VideoCapture(video_file)
    framerate = cap.get(cv2.CAP_PROP_FPS)

    # Define the codec and create a VideoWriter object to save the output video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(temp_video_file, fourcc, framerate, (int(cap.get(3)), int(cap.get(4))))

    time = 0.0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        for start_time, word in words.items():
            if start_time <= time:
                word_to_use = word
            else:
                break

        write_text(word_to_use, frame, out)

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
