import base64
import httpx
from PIL import Image
from io import BytesIO


def download_image(url):
    response = httpx.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.resize((512, 512))
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode()
    return img_b64