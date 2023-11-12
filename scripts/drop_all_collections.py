import pymongo
import os

from dotenv import load_dotenv

load_dotenv()


def drop_all_collections():
    uri = os.environ["MONGO_URI"]
    database_name = os.environ["MONGO_DB"]
    client = pymongo.MongoClient(uri)
    database = client.get_database(database_name)
    for collection_name in database.list_collection_names():
        database.drop_collection(collection_name)


if __name__ == "__main__":
    drop_all_collections()
