import hashlib
import logging
import mimetypes
import os
import smtplib
from email.message import EmailMessage
from enum import Enum

import database
from config import SMTP_HOST, SMTP_PORT, EMAIL_FROM, EMAIL_TO_SEND


class FileStatus(Enum):
    ARRIVED = "ARRIVED"
    SENT = "SENT"


def calculate_hash(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def get_hash(file_hash: str) -> bool:
    try:
        return database.get_file_by_hash(file_hash) is not None
    except Exception:
        logging.exception("Database read error")
        return False


def set_hash(filename: str, file_hash: str, status: FileStatus) -> bool:
    try:
        return database.insert_file(filename, file_hash, status.value)
    except Exception:
        logging.exception("Database insert error")
        return False


def update_status(file_hash: str, status: FileStatus) -> bool:
    try:
        return database.update_status(file_hash, status.value)
    except Exception:
        logging.exception("Database update error")
        return False


def send_email(filepath: str, filename: str) -> bool:
    try:
        msg = EmailMessage()
        msg["Subject"] = f"New CDR file received: {filename}"
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO_SEND

        msg.set_content(
            "A new CDR file has been received.\n"
            f"File: {filename}\n"
        )

        mime_type, _ = mimetypes.guess_type(filepath)
        if mime_type:
            maintype, subtype = mime_type.split("/", 1)
        else:
            maintype, subtype = "application", "octet-stream"

        with open(filepath, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=filename,
            )

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.send_message(msg)

        return True

    except Exception:
        logging.exception("Failed to send email for file %s", filename)
        return False
