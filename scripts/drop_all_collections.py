import pymongo
import os

from dotenv import load_dotenv

load_dotenv()


def drop_all_collections():
    uri = os.environ["MONGO_URI"]
    database_name = os.environ["MONGO_DB"]
    client = pymongo.MongoClient(uri)
    database = client.get_database(database_name)
    collection_names = database.list_collection_names()
    print(f"Found {len(collection_names)} collection(s)")
    for collection_name in database.list_collection_names():
        print(f"Dropping {collection_name}", end="...")
        database.drop_collection(collection_name)
        print("done")


if __name__ == "__main__":
    drop_all_collections()
