import os
import logging
import pymongo

from dotenv import load_dotenv

load_dotenv()


def drop_all_collections():
    uri = os.environ["MONGO_URI"]
    database_name = os.environ["MONGO_DB"]
    client = pymongo.MongoClient(uri)
    database = client.get_database(database_name)
    collection_names = database.list_collection_names()
    logging.info(f"Found {len(collection_names)} collection(s)")
    for collection_name in database.list_collection_names():
        logging.info(f"Dropping {collection_name}", end="...")
        database.drop_collection(collection_name)
        logging.info("done")


if __name__ == "__main__":
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)
    timed_handler = logging.StreamHandler()
    timed_handler.setFormatter(formatter)
    logger.addHandler(timed_handler)
    logger.setLevel(logging.INFO)
    
    drop_all_collections()
