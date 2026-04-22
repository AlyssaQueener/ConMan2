from PIL import Image

img = Image.open("src/thesis.png")
img.thumbnail((200, 200))  # maintains aspect ratio, fits within 200x200
img.save("image-thesis.png")

import cairosvg
from PIL import Image
import io

# Render at high resolution (e.g. 4x)
png_data = cairosvg.svg2png(url="src/u.svg", output_width=800, output_height=800)

# Then downscale with high-quality resampling
#img = Image.open(io.BytesIO(png_data))
#img.thumbnail((200, 200), Image.LANCZOS)
#img.save("thesis_picture-new.png")