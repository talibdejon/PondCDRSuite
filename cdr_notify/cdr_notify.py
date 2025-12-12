import logging
import os
import time

import utils
from config import WATCH_DIR, CHECK_INTERVAL


def main() -> None:
    logging.info("Starting CDR notify service")
    logging.info("Watching directory: %s", WATCH_DIR)

    while True:
        try:
            files = os.listdir(WATCH_DIR)
        except Exception:
            logging.exception("Failed to list directory %s", WATCH_DIR)
            time.sleep(CHECK_INTERVAL)
            continue

        for filename in files:
            full_path = os.path.join(WATCH_DIR, filename)

            if not os.path.isfile(full_path):
                continue

            try:
                file_hash = utils.calculate_hash(full_path)
            except Exception:
                logging.exception("Failed to calculate hash for %s", full_path)
                continue

            if utils.get_hash(file_hash):
                continue

            if not utils.send_email(full_path):
                logging.error("Failed to send email for %s", full_path)
                continue

            utils.set_hash(filename, file_hash, utils.FileStatus.SENT)
            logging.info("File processed successfully: %s", filename)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
