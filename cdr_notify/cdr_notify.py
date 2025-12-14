import logging
import os
import sys

import database
import utils


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    cdr_folder = os.environ.get("CDR_FOLDER", "").strip()
    if not cdr_folder:
        logging.error("CDR_FOLDER is not set")
        return 2

    database.init_db()

    logging.info("Starting CDR notify")
    logging.info("Scanning folder: %s", cdr_folder)

    try:
        files = os.listdir(cdr_folder)
    except Exception:
        logging.exception("Failed to list directory %s", cdr_folder)
        return 1

    for filename in files:
        if filename.startswith("."):
            continue

        full_path = os.path.join(cdr_folder, filename)
        if not os.path.isfile(full_path):
            continue

        try:
            file_hash = utils.calculate_hash(full_path)
        except Exception:
            logging.exception("Failed to calculate hash for %s", filename)
            continue

        if utils.get_hash(file_hash):
            continue

        if not utils.send_email(full_path, filename=filename):
            logging.error("Failed to send email for %s", filename)
            continue

        utils.set_hash(filename, file_hash, utils.FileStatus.SENT)
        logging.info("File processed successfully: %s", filename)

    return 0


if __name__ == "__main__":
    sys.exit(main())