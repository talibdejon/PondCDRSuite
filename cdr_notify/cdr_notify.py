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

    try:
        files = utils.get_files(cdr_folder)
    except Exception:
        logging.exception("Failed to get files")
        return 1

    for full_path in files:
        file_hash = utils.calculate_hash(full_path)
        if not file_hash:
            continue

        if utils.get_hash(file_hash):
            continue

        if not utils.send_email(full_path):
            continue

        filename = os.path.basename(full_path)
        utils.set_hash(filename, file_hash, utils.FileStatus.SENT)
        logging.info("File processed successfully: %s", filename)

    return 0


if __name__ == "__main__":
    sys.exit(main())