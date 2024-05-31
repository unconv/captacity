# Captacity

Add automatic captions to YouTube Shorts (and other videos) using Whisper and MoviePy

## Quick start

```bash
$ python3 main.py <video_file> <output_file>
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

    font = "fonts/Bangers-Regular.ttf",
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
