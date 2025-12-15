import hashlib
import logging
import os
from enum import Enum

import database


class FileStatus(Enum):
    ARRIVED = "ARRIVED"
    SENT = "SENT"


def get_files(cdr_folder: str) -> list[str]:
    try:
        if not os.path.isdir(cdr_folder):
            raise RuntimeError(f"CDR_FOLDER does not exist: {cdr_folder}")

        return [
            os.path.join(cdr_folder, name)
            for name in os.listdir(cdr_folder)
            if os.path.isfile(os.path.join(cdr_folder, name))
        ]
    except Exception:
        logging.exception("Failed to get files from CDR folder")
        return []


def calculate_hash(filepath: str) -> str | None:
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        logging.exception("Failed to calculate hash for %s", filepath)
        return None


def get_hash(file_hash: str) -> bool:
    return database.get_file_by_hash(file_hash) is not None


def set_hash(filename: str, file_hash: str, status: FileStatus) -> bool:
    return database.insert_file(filename, file_hash, status.value)
