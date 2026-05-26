import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
UPLOAD_PRESET = os.getenv("CLOUDINARY_UPLOAD_PRESET")
CLOUDINARY_URL = f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/image/upload"


def upload_image_bytes(image_bytes, mime_type, public_id):
    files = {"file": (public_id, image_bytes, mime_type)}
    data = {"upload_preset": UPLOAD_PRESET, "public_id": public_id}

    response = requests.post(CLOUDINARY_URL, files=files, data=data)
    response.raise_for_status()
    return response.json()["secure_url"]


def upload_image_from_url(image_url, public_id):
    data = {"file": image_url, "upload_preset": UPLOAD_PRESET, "public_id": public_id}

    response = requests.post(CLOUDINARY_URL, data=data)
    response.raise_for_status()
    return response.json()["secure_url"]
