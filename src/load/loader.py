from src.db.mongo import Mongo
from typing import Any


class Loader:
    def __init__(self):
        self.db = Mongo().get_database()

    def upload(self, data: list[dict[str, Any]]) -> None:
        to_upload_locations = {}
        id_references = []
        for i in range(len(data)):
            data[i]["_id"] = data[i].pop("id")
            collection = data[i]["resourceType"]
            to_upload_locations.setdefault(collection, []).append(i)
            id_references.append(
                {"_id": data[i]["_id"], "resourceType": data[i]["resourceType"]}
            )
        for collection, indices in to_upload_locations.items():
            self.db.get_collection(collection).insert_many([data[i] for i in indices])
        self.db.get_collection("IDReference").insert_many(id_references)
