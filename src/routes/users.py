import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.db import get_db
from src.database.model import User
from src.repository import users as repository_users
from src.schemas import UserResponse, UserPasswordUpdate
from src.services import auth as auth_service
from src.services import cloud_image

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch('/avatar', response_model=UserResponse)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
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


#TODO
@router.patch('/update_password', response_model=UserResponse)
async def update_password(body: UserPasswordUpdate,
                          current_user: User = Depends(auth_service.get_current_user),
                          db: Session = Depends(get_db)):
    new_password = None
    if body.password:
        if not body.password == body.confirm_password:
            new_password = body.password

    user = await repository_users.update_password(new_password, current_user, db)
    return user
