import hashlib
import logging
import mimetypes
import os
import smtplib
from email.message import EmailMessage
from enum import Enum
import database


class FileStatus(Enum):
    ARRIVED = "ARRIVED"
    SENT = "SENT"


def calculate_hash(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        logging.exception("Failed to calculate hash for %s", path)
        return ""


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


def send_email(filepath: str, file_hash: str) -> bool:
    try:
        msg = EmailMessage()
        msg["Subject"] = "New CDR File Arrived"
        msg["From"] = "noreply@example.com"
        msg["To"] = "test@example.com"

        msg.set_content("A new CDR file has been arrived to the server.")

        mime_type, _ = mimetypes.guess_type(filepath)
        if mime_type is None:
            maintype = "application"
            subtype = "octet-stream"
        else:
            maintype, subtype = mime_type.split("/", 1)

        with open(filepath, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(filepath)
            )

        server = smtplib.SMTP("localhost", 1026)
        server.send_message(msg)
        server.quit()

        return True

    except Exception:
        logging.exception("Failed to send email for hash %s", file_hash)
        return False
