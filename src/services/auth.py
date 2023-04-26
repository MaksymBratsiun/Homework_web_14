from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import src.repository.users as repository_users
from src.database.db import get_db
from src.conf.config import settings


secret_key = settings.secret_key
algorithm = settings.algorithm

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """
    The verify_password function takes a plain-text password and a hashed password
    and verifies that the two match. It returns True if they do, False otherwise.

    :param plain_password: Store the password that is inputted by the user
    :param hashed_password: Store the hashed password
    :return: True if the password is correct, and false otherwise
    :doc-author: Trelent
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    """
    The get_password_hash function takes a password as an argument and returns the hashed version of that password.
    The hash is generated using the pwd_context object's hash method, which uses bcrypt to generate a secure hash.

    :param password: str: Specify the password that is being hashed
    :return: A hash of the password
    :doc-author: Trelent
    """
    return pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')


async def create_access_token(data: dict, expires_delta: Optional[float] = None):
    """
    The create_access_token function creates a JWT token that is used to authenticate the user.
        The function takes in two arguments: data and expires_delta. Data is a dictionary containing
        information about the user, such as their username and email address. Expires_delta is an optional
        argument that specifies how long the access token will be valid for (in seconds). If no value for
        expires_delta is provided, then it defaults to 15 minutes.

    :param data: dict: Pass the data that will be encoded in the jwt
    :param expires_delta: Optional[float]: Set the expiration time of the access token
    :return: A string that is the encoded access token
    :doc-author: Trelent
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
    encoded_access_token = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_access_token


async def create_refresh_token(data: dict, expires_delta: Optional[float] = None):
    """
    The create_refresh_token function creates a refresh token for the user.
        Args:
            data (dict): A dictionary containing the user's id and username.
            expires_delta (Optional[float]): The number of seconds until the refresh token expires. Defaults to None,
            which is 7 days in seconds.

    :param data: dict: Pass the user's id and username to the function
    :param expires_delta: Optional[float]: Set the expiration time for the token
    :return: An encoded refresh token
    :doc-author: Trelent
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
    encoded_refresh_token = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_refresh_token


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: Session = Depends(get_db)):
    """
    The get_current_user function is a dependency that will be used in the
        protected endpoints. It uses the OAuth2 authorization scheme to get and
        validate JWT tokens. If validation is successful, it returns an object of type User.

    :param token: str: Get the token from the authorization header
    :param db: Session: Pass the database session to the function
    :return: The user object that corresponds to the token payload
    :doc-author: Trelent
    """
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        if payload.get('scope') == 'access_token':
            email = payload.get("sub")
            if email is None:
                raise credentials_exception
        else:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception

    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise credentials_exception
    return user


async def decode_refresh_token(refresh_token: str):
    """
    The decode_refresh_token function is used to decode the refresh token.
    It will raise an HTTPException if the token is invalid or has expired.

    :param refresh_token: str: Pass in the refresh token that is sent to the server
    :return: A payload
    :doc-author: Trelent
    """
    try:
        payload = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
        if payload.get('scope') == 'refresh_token':
            email = payload['sub']
            return email
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid scope for token')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate credentials')


def create_email_token(data: dict):
    """
    The create_email_token function takes a dictionary of data and returns a token.
    The token is encoded with the secret key, algorithm, and expiration date.


    :param data: dict: Pass in the data that will be encoded into the token
    :return: A token that is used to verify the user's email address
    :doc-author: Trelent
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
    token = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return token


def get_email_from_token(token: str):
    """
    The get_email_from_token function takes a token as an argument and returns the email address associated with that
    token. If the token is invalid, it raises an HTTPException.

    :param token: str: Pass the token to the function
    :return: The email from the token
    :doc-author: Trelent
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        if payload.get('scope') == 'email_token':
            email = payload['sub']
            return email
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid scope for token')

    except JWTError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail='Invalid token for email verification')

