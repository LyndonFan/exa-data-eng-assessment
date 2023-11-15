import logging
import orjson
from fhir.resources.R4B.resource import Resource

from src.db.mongo import Mongo


class BaseProcessor:
    def __init__(self):
        self.mongo = Mongo()

    def process_data_for_mongo(
        self, data: list[Resource]
    ) -> tuple[str, list[dict], list[dict]]:
        resource_type = data[0].resource_type
        to_save_data = [orjson.loads(d.json(return_bytes=True)) for d in data]
        for i in range(len(to_save_data)):
            to_save_data[i]["_id"] = to_save_data[i].pop("id")
            to_save_data[i].pop("resourceType")
        id_references = [
            {"_id": d["_id"], "resource_type": resource_type} for d in to_save_data
        ]
        return resource_type, to_save_data, id_references

    def upload_to_mongo(
        self, resource_type: str, to_save_data: list[dict], id_references: list[dict]
    ):
        self.mongo.get_database().get_collection(resource_type).insert_many(
            to_save_data
        )
        self.mongo.get_database().get_collection("IDReference").insert_many(
            id_references
        )

    def process(self, data: list[Resource]):
        if not data:
            return
        logging.info(f"Start processing {len(data)} {data[0].resource_type}")
        resource_type, to_save_data, id_references = self.process_data_for_mongo(data)
        logging.info(f"Start uploading to mongo for {resource_type}")
        self.upload_to_mongo(resource_type, to_save_data, id_references)
