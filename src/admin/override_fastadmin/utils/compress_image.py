from io import BytesIO
import PIL
from PIL import Image, ImageOps

NEED_HEIGHT_OF_PHOTO_PX = 600

def compress_image(image: BytesIO, format: str) -> BytesIO:
    with Image.open(image) as pill_image:
        image_height = pill_image.height
        image_width = pill_image.width

        ratio = image_height / image_width

        new_image_width = int(NEED_HEIGHT_OF_PHOTO_PX / ratio)
        pill_image = pill_image.resize(
            (
                new_image_width,
                NEED_HEIGHT_OF_PHOTO_PX
            ),
            PIL.Image.NEAREST
        )
        pill_image = ImageOps.exif_transpose(pill_image)
        new_image = BytesIO()
        pill_image.save(
            new_image,
            format,
            optimize=True
        )
        new_image.seek(0)
        return new_image

