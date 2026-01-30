from typing import List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr

from app.config import config


class EmailSchema(BaseModel):
    email: List[EmailStr]

conf = ConnectionConfig(
    MAIL_USERNAME = config("MAIL_USERNAME", default="user"),
    MAIL_PASSWORD = config("MAIL_PASSWORD", default="password"),
    MAIL_FROM = config("MAIL_FROM", default="admin@example.com"),
    MAIL_PORT = config("MAIL_PORT", default=587, cast=int),
    MAIL_SERVER = config("MAIL_SERVER", default="smtp.gmail.com"),
    MAIL_FROM_NAME = config("MAIL_FROM_NAME", default="AI Generator App"),
    MAIL_STARTTLS = config("MAIL_STARTTLS", default=True, cast=bool),
    MAIL_SSL_TLS = config("MAIL_SSL_TLS", default=False, cast=bool),
    USE_CREDENTIALS = config("USE_CREDENTIALS", default=True, cast=bool),
    VALIDATE_CERTS = config("VALIDATE_CERTS", default=True, cast=bool)
)

async def send_email_async(subject: str, email_to: List[str], body: str):
    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        body=body,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)
