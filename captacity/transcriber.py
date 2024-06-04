import openai
from openai._types import FileTypes

def transcribe_with_api(
    audio_file: FileTypes,
    prompt: str | None = None
):
    """
    Transcribe an audio file using the OpenAI Whisper API
    """
    transcript = openai.audio.transcriptions.create(
        model="whisper-1",
        file=open(audio_file, "rb"),
        response_format="verbose_json",
        timestamp_granularities=["segment", "word"],
        prompt=prompt,
    )

    # Add space to beginning of words
    # to match local Whisper format
    for word in transcript.words:
        word["word"] = " " + word["word"]

    # Return response in same format
    # as local Whisper format
    return [{
        "start": transcript.segments[0]["start"],
        "end": transcript.segments[-1]["end"],
        "words": transcript.words,
    }]

def transcribe_locally(
    audio_file: str,
    prompt: str | None = None
):
    """
    Transcribe an audio file using the local Whisper package
    (https://pypi.org/project/openai-whisper/)
    """
    import whisper

    model = whisper.load_model("base")

    transcription = model.transcribe(
        audio=audio_file,
        word_timestamps=True,
        fp16=False,
        initial_prompt=prompt,
    )

    return transcription["segments"]
