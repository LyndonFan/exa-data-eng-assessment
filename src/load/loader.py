import os
from typing import Any
import urllib.parse
import pymongo

from dotenv import load_dotenv

load_dotenv()

class Mongo:
    _instance = None

    def __new__(cls) -> "Mongo":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        uri_to_format = os.getenv("MONGODB_URI", "")
        uri_to_format = uri_to_format.replace("<user>", "%s")
        uri_to_format = uri_to_format.replace("<password>", "%s")
        self.client = pymongo.MongoClient(
            uri_to_format.format(
                urllib.parse.quote_plus(os.getenv("MONGODB_USERNAME", "")),
                urllib.parse.quote_plus(os.getenv("MONGODB_PASSWORD", "")),
            )
        )

class Loader:
    def __init__(self):
        self.db = Mongo()
    
    def upload(self, data: list[dict[str, Any]]) -> None:
        to_upload_locations = {}
        for i in range(len(data)):
            data[i]["_id"] = data[i]["id"]
            collection = data[i]["resourceType"]
            to_upload_locations.setdefault(collection, []).append(i)
        for collection, indices in to_upload_locations.items():
            self.db.client.get_database("exa-data")[collection].insert_many(data[indices])