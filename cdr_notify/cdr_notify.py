import logging
import os
import time

import utils
from config import CDR_FOLDER, CHECK_INTERVAL


def main() -> None:
    logging.info("Starting CDR notify service")
    logging.info("Watching folder: %s", CDR_FOLDER)

    while True:
        try:
            files = os.listdir(CDR_FOLDER)
            logging.info("Files detected: %s", files)
        except Exception:
            logging.exception("Failed to list directory %s", CDR_FOLDER)
            time.sleep(CHECK_INTERVAL)
            continue

        for filename in files:
            full_path = os.path.join(CDR_FOLDER, filename)

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

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
