from fastapi import Depends
from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.model import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User | None:
    """
    The get_user_by_email function takes in an email and a database session,
    and returns the user with that email if it exists. If no such user exists,
    it returns None.

    :param email: str: Specify the email of the user we want to get
    :param db: Session: Pass the database session to the function
    :return: The first user with a matching email address
    :doc-author: Trelent
    """
    return db.query(User).filter_by(email=email).first()


async def create_user(body: UserModel, db: Session = Depends(get_db)):
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Specify the type of data that will be passed to the function
    :param db: Session: Get a database session
    :return: A user object
    :doc-author: Trelent
    """
    g = Gravatar(body.email)
    new_user = User(**body.dict(), avatar=g.get_image())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token, db: Session):
    """
    The update_token function updates the refresh token for a user in the database.
        Args:
            user (User): The User object to update.
            refresh_token (str): The new refresh token to store in the database.
            db (Session): A connection to our Postgres database.

    :param user: User: Identify the user that is being updated
    :param refresh_token: Update the refresh_token in the database
    :param db: Session: Pass the database session to the function
    :return: The user with the updated refresh_token
    :doc-author: Trelent
    """
    user.refresh_token = refresh_token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Get the email of the user that is trying to confirm their account
    :param db: Session: Pass in the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: Find the user in the database
    :param url: str: Specify the type of data that is being passed into the function
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
