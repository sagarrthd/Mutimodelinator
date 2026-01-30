import os
import asyncio
from celery import Celery
from app.config import REDIS_URL
from app.email import send_email_async

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task
def send_welcome_email(email: str):
    """Send welcome email using async function in sync task."""
    subject = "Welcome to AI Generator"
    body = f"<h1>Welcome!</h1><p>Thanks for registering with email: {email}</p>"

    try:
        # Run async function in sync context
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(
            send_email_async(subject, [email], body)
        )
        return f"Welcome email sent to {email}"
    except Exception as e:
        return f"Failed to send email: {e}"
