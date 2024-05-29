from moviepy.editor import TextClip, ImageClip, VideoClip
from PIL import Image, ImageFilter
import numpy
import tempfile

def moviepy_to_pillow(clip) -> Image:
    temp_file = tempfile.NamedTemporaryFile(suffix=".png").name
    clip.save_frame(temp_file)
    image = Image.open(temp_file)
    return image

def get_text_size(text, fontsize, font, stroke_width):
    text_clip = TextClip(text, fontsize=fontsize, color="white", font=font, stroke_width=stroke_width)
    pil_img = moviepy_to_pillow(text_clip)
    return pil_img.size

def create_text(text, fontsize, color, font, bg_color='transparent', blur_radius: int=0, opacity=1, stroke_color=None, stroke_width=1, kerning=0) -> VideoClip:
    text_clip = TextClip(text, fontsize=fontsize, color=color, bg_color=bg_color, font=font, stroke_color=stroke_color, stroke_width=stroke_width, kerning=kerning)

    text_clip = text_clip.set_opacity(opacity)

    if blur_radius:
        # Convert TextClip to a PIL image
        pil_img = moviepy_to_pillow(text_clip)

        # Offset blur to make it centered
        offset = int(blur_radius * 0.6)

        # Add empty space around text for blur
        pil_img_padded = Image.new("RGBA", (pil_img.width + blur_radius * 3, pil_img.height + blur_radius * 3))
        pil_img_padded.paste(moviepy_to_pillow(text_clip), (blur_radius+offset, blur_radius+offset))

        # Create a blurred version of the text
        pil_img_padded = pil_img_padded.filter(
            ImageFilter.GaussianBlur(radius=blur_radius)
        )

        text_clip = ImageClip(numpy.array(pil_img_padded))
        text_clip = text_clip.set_duration(text_clip.duration)

    return text_clip
