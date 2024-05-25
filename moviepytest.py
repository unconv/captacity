from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
from moviepy.video.tools.drawing import color_gradient
from PIL import Image, ImageFilter
import numpy
import tempfile

# Load the video
video = VideoFileClip("test.avi")

def moviepy_to_pillow(clip) -> Image:
    temp_file = tempfile.NamedTemporaryFile(suffix=".png").name
    clip.save_frame(temp_file)
    image = Image.open(temp_file)
    image.save("test.png")
    return image

# Create the shadow as an image using PIL
def create_text(text, fontsize, color, font, bg_color='transparent', blur_radius=0, opacity=1, stroke_color=None, stroke_width=1, kerning=0):
    text_clip = TextClip(text, fontsize=fontsize, color=color, bg_color=bg_color, font=font, stroke_color=stroke_color, stroke_width=stroke_width, kerning=kerning)

    text_clip = text_clip.set_opacity(opacity)

    if blur_radius:
        # Convert TextClip to a PIL image
        pil_img = moviepy_to_pillow(text_clip)

        # Create a blurred version of the text
        pil_img = pil_img.filter(
            ImageFilter.GaussianBlur(radius=blur_radius)
        )

        text_clip = ImageClip(numpy.array(pil_img))
        text_clip = text_clip.set_duration(text_clip.duration)

    return text_clip

text_to_draw = "SUBSCRIBE!"
font = "fonts/Bangers-Regular.ttf"

# Create the text clip
text = create_text(text_to_draw, fontsize=120, color="#35dc0a", font=font, stroke_color="black", stroke_width=2)
text = text.set_duration(video.duration)
text = text.set_position(("center", "center"))

# Create the shadow clip
shadow_clip = create_text(text_to_draw, fontsize=120, color="white", font=font, blur_radius=6, opacity=1)
shadow_clip = shadow_clip.set_duration(video.duration)
shadow_clip = shadow_clip.set_position(("center", "center"))

# Composite the shadow and the text onto the video
video_with_text = CompositeVideoClip([video, shadow_clip, shadow_clip, shadow_clip, text])

exit(video_with_text.save_frame("output.png"))

# Write the result to a file
video_with_text.write_videofile("output_video.mp4", codec="libx264", fps=24)
