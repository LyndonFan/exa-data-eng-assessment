import orjson
from fhir.resources.R4B.resource import Resource

from src.db.mongo import Mongo

class BaseProcessor:
    def __init__(self):
        self.mongo = Mongo()
    
    def save_to_mongo(self, data: list[Resource]):
        resource_type = data[0].resource_type
        to_save_data = [
            orjson.loads(d.json(return_bytes=True)) for d in data
        ]
        for i in range(len(to_save_data)):
            to_save_data[i]["_id"] = to_save_data[i].pop("id")
            to_save_data[i].pop("resource_type")
        self.mongo.get_database().get_collection(resource_type).insert_many(to_save_data)
        id_references = [
            {"_id": d["id"], "resource_type": resource_type}
            for d in to_save_data
        ]
        self.mongo.get_database().get_collection("IDReference").insert_many(
            id_references
        )
    
    def process(self, data: list[Resource]):
        self.save_to_mongo(data)