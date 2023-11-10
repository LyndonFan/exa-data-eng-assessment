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
        uri_to_format = os.getenv("MONGO_URI", "")
        uri_to_format = uri_to_format.replace("<user>", "{user}")
        uri_to_format = uri_to_format.replace("<password>", "{password}")
        uri = uri_to_format.format(
            user=urllib.parse.quote_plus(os.getenv("MONGO_USER", "")),
            password=urllib.parse.quote_plus(os.getenv("MONGO_PASSWORD", "")),
        )
        self.client = pymongo.MongoClient(uri)
    
    def get_database(self) -> pymongo.database.Database:
        return self.client.get_database("exa-data")

class Loader:
    def __init__(self):
        self.db = Mongo().get_database()
    
    def upload(self, data: list[dict[str, Any]]) -> None:
        to_upload_locations = {}
        id_references = []
        for i in range(len(data)):
            if "id" in data[i]:
                data[i]["_id"] = data[i]["id"]
            else:
                print(f"Missing id for {i}th entry")
            if "resourceType" not in data[i]:
                raise ValueError(f"Missing resourceType for {i}th entry: {data[i]}")
            collection = data[i]["resourceType"]
            to_upload_locations.setdefault(collection, []).append(i)
            id_references.append({"_id": data[i]["_id"], "resourceType": data[i]["resourceType"]})
        for collection, indices in to_upload_locations.items():
            self.db.get_collection(collection).insert_many([
                data[i] for i in indices
            ])
        self.db.get_collection("IDReferences").insert_many(id_references)