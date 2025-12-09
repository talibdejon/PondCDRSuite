from enum import Enum
import hashlib
import logging
import os
import smtplib
import sqlite3
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

import database


# Length of returned hash in hex characters; 64 = full SHA-256.
HASH_LENGTH: int = 64

# These can be overridden via environment or directly in code if needed.
EMAIL_TO_SEND: str = os.getenv("EMAIL_TO_SEND", "")
SMTP_SERVER: str = os.getenv("SMTP_SERVER", "")
SMTP_PORT: str = os.getenv("SMTP_PORT", "")

BASE_DIR: Path = Path(__file__).resolve().parent
RESOURCES_DIR: Path = BASE_DIR / "resources"


class FileStatus(Enum):
    ARRIVED = "Arrived"
    SENT = "Sent"
    DELIVERED = "Delivered"
    REMOVED = "Removed"


# ---------------------------------------------------------------------------
# Template helpers
# ---------------------------------------------------------------------------

def _read_resource(name: str) -> str:
    """
    Read a text file from the resources directory.
    """
    path = RESOURCES_DIR / name
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------

def calculate_hash(filename: str) -> str:
    """
    Accept a filename and return a deterministic SHA-256 hash string.
    """
    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("filename must be a non-empty string")

    normalized = filename.strip().encode("utf-8")
    digest = hashlib.sha256(normalized).hexdigest()

    return digest[:HASH_LENGTH] if HASH_LENGTH > 0 else digest


# ---------------------------------------------------------------------------
# Database-related helpers
# ---------------------------------------------------------------------------

def get_hash(file_hash: str) -> Optional[sqlite3.Row]:
    """
    Accept a hash and return the corresponding row from the database.
    """
    return database.fetch_by_hash(file_hash)


def set_hash(filename: str, status: FileStatus) -> int:
    """
    Accept a filename and add its hash to the database.
    Returns the inserted record id.
    """
    file_hash = calculate_hash(filename)
    return database.insert_record(filename, file_hash, status.value)


def update_status(file_hash: str, status: FileStatus) -> bool:
    """
    Accept a hash and a new status. Return True on success.
    """
    return database.update_status(file_hash, status.value)


# ---------------------------------------------------------------------------
# Email helper
# ---------------------------------------------------------------------------

def send_email(filename: str) -> bool:
    """
    Accept a filename and send an email with the file attached.
    Return True on success, False on failure.
    """
    if not EMAIL_TO_SEND:
        raise RuntimeError("EMAIL_TO_SEND is not set")
    if not SMTP_SERVER:
        raise RuntimeError("SMTP_SERVER is not set")
    if not SMTP_PORT:
        raise RuntimeError("SMTP_PORT is not set")

    try:
        port = int(SMTP_PORT)
    except ValueError:
        raise RuntimeError(f"Invalid SMTP_PORT value: {SMTP_PORT}")

    smtp_user = os.getenv("SMTP_USERNAME", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")
    smtp_from = os.getenv("SMTP_FROM", smtp_user or EMAIL_TO_SEND)
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
    use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() in ("1", "true", "yes")

    basename = os.path.basename(filename)

    # Load templates (fallback to simple ones if files not found)
    try:
        subject_template = _read_resource("email_subject.txt")
        body_template = _read_resource("email_body.txt")
    except FileNotFoundError:
        subject_template = "CDR file {filename}"
        body_template = "File {filename} has been processed."

    context = {"filename": basename}
    subject = subject_template.format(**context).strip()
    body = body_template.format(**context)

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = smtp_from
    msg["To"] = EMAIL_TO_SEND
    msg.attach(MIMEText(body, _charset="utf-8"))

    # Attach file if it exists
    file_path = Path(filename)
    if file_path.is_file():
        try:
            with file_path.open("rb") as f:
                part = MIMEApplication(f.read(), Name=file_path.name)
            part["Content-Disposition"] = f'attachment; filename="{file_path.name}"'
            msg.attach(part)
        except OSError as e:
            logging.warning("Failed to attach file '%s': %s", filename, e)

    logging.info(
        "Sending email about file '%s' to '%s' via %s:%s",
        basename,
        EMAIL_TO_SEND,
        SMTP_SERVER,
        SMTP_PORT,
    )

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(SMTP_SERVER, port, timeout=30)
        else:
            server = smtplib.SMTP(SMTP_SERVER, port, timeout=30)

        with server:
            server.ehlo()
            if use_tls and not use_ssl:
                server.starttls()
                server.ehlo()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        logging.info("Email sent successfully for file '%s'", basename)
        return True
    except Exception as e:
        logging.exception("Failed to send email for file '%s': %s", basename, e)
        return False
