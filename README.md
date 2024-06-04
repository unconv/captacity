# Captacity

Add automatic captions to YouTube Shorts (and other videos) using Whisper and MoviePy

## Quick start

```bash
$ pip install captacity
$ captacity <video_file> <output_file>
```

## Programmatic use

```python
import captacity

captacity.add_captions(
    video_file="my_short.mp4",
    output_file="my_short_with_captions.mp4",
)
```

## Custom configuration

```python
import captacity

captacity.add_captions(
    video_file="my_short.mp4",
    output_file="my_short_with_captions.mp4",

    font = "/path/to/your/font.ttf",
    font_size = 130,
    font_color = "yellow",

    stroke_width = 3,
    stroke_color = "black",

    shadow_strength = 1.0,
    shadow_blur = 0.1,

    highlight_current_word = True,
    word_highlight_color = "red",

    line_count=1,

    padding = 50,
)
```

## Using Whisper locally

By default, OpenAI Whisper is used locally if the `openai-whisper` package is installed. Otherwise, the OpenAI Whisper API is used. If you want to force the use of the API, you can specify `use_local_whisper=False` in the arguments to `captacity.add_captions`:

```python
import captacity

captacity.add_captions(
    video_file="my_short.mp4",
    output_file="my_short_with_captions.mp4",
    use_local_whisper=False,
)
```

You can install Captacity with `pip install captacity[local_whisper]` to install Whisper locally as well.
