#!/usr/bin/env python3
"""
Send an email notification with the attachment for any new file in the CDR folder.

Workflow for each file in CDR_FOLDER:

1) Calculate hash = utils.calculate_hash(filename)
2) Check existing record = utils.get_hash(hash)
   - If record exists (file already in database) → skip
   - If record does not exist (new file):
       a) Insert with status Arrived: utils.set_hash(filename, utils.FileStatus.ARRIVED)
       b) Send email: utils.send_email(full_path_to_file)
       c) If email sent successfully → update status to Sent:
          utils.update_status(hash, utils.FileStatus.SENT)
"""

import logging
import os
from pathlib import Path

import database
import utils

# CDR folder to scan. Can be overridden by the CDR_FOLDER environment variable.
CDR_FOLDER: str = os.getenv("CDR_FOLDER", "")


def process_cdr_folder() -> None:
    """
    Scan the CDR folder and process new files.
    """
    if not CDR_FOLDER:
        raise RuntimeError(
            "CDR_FOLDER is not configured. "
            "Set CDR_FOLDER in environment or in cdr_notify.py."
        )

    folder = Path(CDR_FOLDER).expanduser().resolve()

    if not folder.exists() or not folder.is_dir():
        raise RuntimeError(f"CDR_FOLDER does not exist or is not a directory: {folder}")

    logging.info("Scanning CDR folder: %s", folder)

    for entry in sorted(folder.iterdir()):
        if not entry.is_file():
            continue

        filename = entry.name
        full_path = str(entry)

        # 1) Calculate hash from filename
        try:
            file_hash = utils.calculate_hash(filename)
        except Exception:
            logging.exception("Failed to calculate hash for file '%s'", filename)
            continue

        # 2) Check if hash already exists in database
        try:
            existing = utils.get_hash(file_hash)
        except Exception:
            logging.exception("Database error while checking hash for file '%s'", filename)
            continue

        if existing:
            logging.debug("File already in database, skipping: %s", filename)
            continue

        logging.info("New file detected: %s", filename)

        # 3a) Insert with status Arrived
        try:
            utils.set_hash(filename, utils.FileStatus.ARRIVED)
        except Exception:
            logging.exception("Failed to insert record for file '%s'", filename)
            continue

        # 3b) Send email with attachment
        email_sent = False
        try:
            email_sent = utils.send_email(full_path)
        except Exception:
            logging.exception("Failed to send email for file '%s'", filename)

        # 3c) If email was sent successfully, update status to Sent
        if email_sent:
            try:
                updated = utils.update_status(file_hash, utils.FileStatus.SENT)
                if not updated:
                    logging.warning(
                        "Status not updated to SENT for file '%s' (hash=%s)", filename, file_hash
                    )
            except Exception:
                logging.exception("Failed to update status to SENT for file '%s'", filename)
        else:
            logging.warning(
                "Email was not sent successfully for file '%s'; status will remain ARRIVED", filename
            )


def main() -> None:
    """
    Entry point for the script.
    """
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    logging.info("Starting cdr_notify run")

    # Ensure DB and table exist
    database.init_db()

    process_cdr_folder()
    logging.info("cdr_notify run finished")


if __name__ == "__main__":
    main()



### Send a email notification with the attachement on any new file in the CDR folder

import utils

# CDR_FOLDER=""

# For any file in the CDR_FOLDER:
# Calculate hash = utils.calculate_hash(filename)
# Check is utils.get_hash(hash)
# If it returns True (file found in the database), skip it and go to the next file
# It it returns False (new file found):
#   1) Put it to the database with the Arrived status - utils.set_hash(filename, utils.FileStatus.ARRIVED) 
#   2) Send email - utils.send_email(filename)
#   3) Change status to Sent - utils.update_status(hash, utils.FileStatus.SENT)
#   4) Go to the next file