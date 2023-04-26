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
    """
    The generate_image_name function takes an email address as input and returns a unique image name.
    The function uses the hashlib library to generate a SHA256 hash of the email address, then truncates it to 16 characters.
    This ensures that each user has a unique image name.

    :param email: str: Specify the type of data that will be passed into the function
    :return: A string of 16 characters
    :doc-author: Trelent
    """
    image_name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:16]
    return image_name


def upload_image(file, public_id: str):
    """
    The upload_image function takes a file and public_id as arguments.
    The function then uploads the file to Cloudinary using the public_id provided.

    :param file: Specify the file to upload
    :param public_id: str: Set the public id of the image
    :return: A dictionary containing the public_id and url of the uploaded image
    :doc-author: Trelent
    """
    r = cloudinary.uploader.upload(file, public_id=f'app_note_auth/{public_id}', overwrite=True)
    return r


def get_avatar_url(public_id: str, r):
    """
    The get_avatar_url function takes in a public_id and an r (which is the result of a cloudinary.api.resource call)
    and returns the URL for that image, with width=250, height=250, crop='fill',
    and version set to whatever was returned by the resource call.

    :param public_id: str: Specify the public id of the image to be fetched
    :param r: Get the version of the image
    :return: A url to the avatar image
    :doc-author: Trelent
    """
    src_url = cloudinary.CloudinaryImage(f'app_note_auth/{public_id}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    return src_url
