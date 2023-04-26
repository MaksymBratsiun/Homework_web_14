from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services import auth as auth_service
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.email_username,
    MAIL_PASSWORD=settings.email_password,
    MAIL_FROM=EmailStr(settings.email_from),
    MAIL_PORT=settings.email_port,
    MAIL_SERVER=settings.email_server,
    MAIL_FROM_NAME="Contacts book App",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to confirm their email address.
        The function takes in three parameters:
            -email: EmailStr, the user's email address that they entered when signing up for an account.
            -username: str, the username of the user who is trying to sign up for an account. This will be used in
                conjunction with host (see below) and token_verification (see below) as part of a URL that will be sent
                via email to verify their identity and allow them access into our application.

    :param email: EmailStr: Specify the email address of the user
    :param username: str: Personalize the email
    :param host: str: Pass the host of the application to the template
    :return: A coroutine object
    :doc-author: Trelent
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)
