import hashlib

import cloudinary.uploader

from src.conf.config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)


def generate_image_name(email: str):
    image_name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:16]
    return image_name


def upload_image(file, public_id: str):
    r = cloudinary.uploader.upload(file, public_id=f'app_note_auth/{public_id}', overwrite=True)
    return r


def get_avatar_url(public_id: str, r):
    src_url = cloudinary.CloudinaryImage(f'app_note_auth/{public_id}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    return src_url
