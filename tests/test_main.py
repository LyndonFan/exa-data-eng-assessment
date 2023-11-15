import pytest
from typing import Optional
import polars as pl
from pathlib import Path
from main import main

@pytest.fixture
def mock_mongo(mocker):
    class MockCollection:
        def __init__(self):
            self.values = {}
        def insert_one(self, value):
            if value["_id"] in self.values:
                raise ValueError(f"Duplicate key: {value['_id']}")
            self.values[value["_id"]] = value
        def insert_many(self, values):
            new_keys = set(value["_id"] for value in values)
            if new_keys & set(self.values.keys()):
                raise ValueError(f"Duplicate key(s): {new_keys & set(self.values.keys())}")
            self.values.update({value["_id"]: value for value in values})
    
    class MockDatabase:
        def __init__(self):
            self.collections = {}
        def get_collection(self, collection_name):
            if collection_name not in self.collections:
                self.collections[collection_name] = MockCollection()
            return self.collections[collection_name]

    class MockMongo:
        databases = {}
        def __init__(self):
            pass

        def get_database(self, database_name="test"):
            if database_name not in self.databases:
                self.databases[database_name] = MockDatabase()
            return self.databases[database_name]
    
    mocker.patch("src.db.mongo.Mongo", return_value=MockMongo())

@pytest.fixture
def mock_sql(mocker):
    class MockPSQL:
        values = {}
        def __init__(self):
            self._connection = None
        def connect(self):
            if self._connection is None:
                self._connection = mocker.Mock()
        def connection(self):
            if self._connection is None:
                self.connect()
            return self._connection
        def disconnect(self):
            if self._connection is not None:
                self._connection = None
        def execute_query(self, query, fetch: bool = False):
            pass
        def copy_into_table(
            self,
            table_name: str,
            df: pl.DataFrame,
            json_columns: Optional[list[str]] = None,
        ):
            if table_name in self.values:
                self.values[table_name] = pl.concat([
                    self.values[table_name], df
                ])
            else:
                self.values[table_name] = df
        
    mocker.patch("src.db.postgresql.PostgreSQL", return_value=MockPSQL())
    return MockPSQL

def test_main(mock_mongo, mock_sql):
    main(Path("tests/fixtures/bundle_transaction.json"))