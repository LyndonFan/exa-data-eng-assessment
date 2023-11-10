import pymongo
import os
import urllib.parse

from dotenv import load_dotenv

load_dotenv()

def drop_all_collections():
    uri_to_format = os.getenv("MONGO_URI", "")
    uri_to_format = uri_to_format.replace("<user>", "{user}")
    uri_to_format = uri_to_format.replace("<password>", "{password}")
    uri = uri_to_format.format(
        user=urllib.parse.quote_plus(os.getenv("MONGO_USER", "")),
        password=urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD", "")),
    )
    client = pymongo.MongoClient(uri)
    database = client.get_database("exa-data")
    for collection_name in database.list_collection_names():
        database.drop_collection(collection_name)

if __name__ == "__main__":
    drop_all_collections()