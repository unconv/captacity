# Captacity

Add automatic captions to YouTube Shorts (and other videos) using Whisper and MoviePy

## Quick start

```bash
$ python3 captacity.py <video_file> [output_file]
```

## Programmatic use

```python
import captacity

captacity.add_captions(
    video_file="my_short.mp4",
    output_file="my_short_with_captions.mp4",
)
```
