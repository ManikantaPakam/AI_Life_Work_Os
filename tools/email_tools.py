import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from langchain_core.tools import tool

from database import get_connection

load_dotenv()


@tool
def draft_email(
    recipient: str,
    subject: str,
    body: str,
) -> str:
    """
    Create an email draft and save it in PostgreSQL.
    Does not send the email.
    """

    with get_connection() as connection:
        email = connection.execute(
            """
            INSERT INTO emails (
                recipient,
                subject,
                body,
                status
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (recipient, subject, body, "draft"),
        ).fetchone()

    return (
        f"Email draft saved successfully.\n"
        f"Email ID: {email['id']}\n"
        f"To: {recipient}\n"
        f"Subject: {subject}\n\n"
        f"{body}"
    )


@tool
def send_email(
    recipient: str,
    subject: str,
    body: str,
) -> str:
    """
    Send an email and save its status in PostgreSQL.

    Use only when the user explicitly asks to send an email.
    """

    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv(
        "SMTP_SERVER",
        "smtp.gmail.com",
    )
    smtp_port = int(
        os.getenv("SMTP_PORT", "587")
    )

    if not sender or not password:
        return "Email configuration is missing."

    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(
            smtp_server,
            smtp_port,
            timeout=30,
        ) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(message)

    except Exception as error:
        return f"Failed to send email: {error}"

    with get_connection() as connection:
        email = connection.execute(
            """
            INSERT INTO emails (
                recipient,
                subject,
                body,
                status,
                sent_at
            )
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
            """,
            (
                recipient,
                subject,
                body,
                "sent",
            ),
        ).fetchone()

    return (
        f"Email sent successfully.\n"
        f"Email ID: {email['id']}\n"
        f"To: {recipient}\n"
        f"Subject: {subject}"
    )