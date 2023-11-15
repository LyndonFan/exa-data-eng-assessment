import os
import argparse
import logging
from pathlib import Path

from src.extract import Extractor
from src.process import ProcessorFactory

from dotenv import load_dotenv
load_dotenv()

def main(filepath: Path) -> None:
    logging.info(f"Start processing {filepath}")
    documents = []
    if filepath.is_dir():
        for path in filepath.rglob("*.json"):
            logging.info(f"Processing {path}")
            logging.info("Extracting...")
            data = Extractor().extract(path)
            logging.info(f"Done for {path}")
            documents.extend(data)
    elif filepath.is_file() and filepath.suffix == ".json":
        logging.info(f"Processing {filepath}")
        logging.info("Extracting...")
        data = Extractor().extract(filepath)
        documents = data
        logging.info("Done")
    else:
        raise ValueError(f"Unsupported file type: {filepath}")
    logging.info("Processing & Uploading...")
    ProcessorFactory.batch_process(documents)
    logging.info("Done")


if __name__ == "__main__":
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)
    timed_handler = logging.StreamHandler()
    timed_handler.setFormatter(formatter)
    logger.addHandler(timed_handler)
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        help="Path to the json file or directory of them to process",
        type=str
    )
    args = parser.parse_args()
    main(Path(args.path))