import os
import logging
import database
import utils

CDR_FOLDER = ""


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    logging.info("Starting cdr_notify")

    if not os.path.isdir(CDR_FOLDER):
        logging.error("Folder does not exist: %s", CDR_FOLDER)
        return

    logging.info("Scanning folder: %s", CDR_FOLDER)

    database.init_db()

    files = [f for f in os.listdir(CDR_FOLDER)]
    logging.info("Files detected: %s", files)

    for filename in files:
        full_path = os.path.join(CDR_FOLDER, filename)

        if not os.path.isfile(full_path):
            continue

        file_hash = utils.calculate_hash(full_path)
        if not file_hash:
            continue

        if utils.get_hash(file_hash):
            logging.info("Already processed: %s", filename)
            continue

        logging.info("New file detected: %s", filename)

        utils.set_hash(filename, file_hash, utils.FileStatus.ARRIVED)

        if utils.send_email(full_path, file_hash):
            utils.update_status(file_hash, utils.FileStatus.SENT)
            logging.info("Status updated to SENT for %s", filename)

    logging.info("cdr_notify finished")


if __name__ == "__main__":
    main()
