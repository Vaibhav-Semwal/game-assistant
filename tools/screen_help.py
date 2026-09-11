import io
import mss
import base64
from PIL import Image

def capture_screen() -> Image.Image:
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
        image = Image.frombytes("RGB",screenshot.size,screenshot.rgb)
        return image


def image_to_base64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(
        buffer,
        format="JPEG",
        quality=85
    )
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return encoded
