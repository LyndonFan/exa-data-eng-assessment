import os
from typing import Any, Optional
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
        self.client = pymongo.MongoClient(os.environ["MONGO_URI"])
        self.database_name = os.environ["MONGO_DB"]

    def get_database(self, database_name: Optional[str] = None) -> pymongo.database.Database:
        if database_name is None:
            database_name = self.database_name
        return self.client.get_database(database_name)