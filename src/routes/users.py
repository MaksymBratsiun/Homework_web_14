import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.database.model import User
from src.repository import users as repository_users
from src.schemas import UserResponse
from src.services import auth as auth_service
from src.services import cloud_image

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function is a GET request that returns the current user's information.
        It requires authentication, and it uses the auth_service to get the current user.

    :param current_user: User: Tell fastapi that the function expects a user object
    :return: The current_user object
    :doc-author: Trelent
    """
    return current_user


@router.patch('/avatar', response_model=UserResponse)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function updates the avatar of a user.
        Args:
            file (UploadFile): The image to be uploaded.
            current_user (User): The user whose avatar is being updated.  This is passed in by the auth_service
                dependency, which uses JWT authentication to get the current user from their token's payload and pass it
                into this function as an argument.  If no valid token was provided, then this will return None instead
                of a User object, and thus raise an HTTPException with status code 401 Unauthorized because there was
                no valid authorization header present in the request that contained a JWT token with

    :param file: UploadFile: Upload the file to cloudinary
    :param current_user: User: Get the current user from the database
    :param db: Session: Get the database session
    :return: The updated user
    :doc-author: Trelent
    """
    cloudinary.config(
            cloud_name=settings.cloudinary_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secure=True
    )
    public_id = cloud_image.generate_image_name(current_user.email)
    r = cloud_image.upload_image(file.file, public_id)
    src_url = cloud_image.get_avatar_url(public_id, r)
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
