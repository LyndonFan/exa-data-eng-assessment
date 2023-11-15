import pytest

import os
import shutil
from datetime import datetime
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
        def __init__(self):
            self.databases = {}
            pass
        
        def get_database(self, database_name="test"):
            if database_name not in self.databases:
                self.databases[database_name] = MockDatabase()
            return self.databases[database_name]
    mongo = MockMongo()
    mocker.patch("src.db.mongo.Mongo", return_value=mongo)
    mocker.patch("src.process.base_processor.Mongo", return_value=mongo)
    return mongo

@pytest.fixture
def mock_sql(mocker):
    class MockPSQL:
        def __init__(self):
            self._connection = None
            self.tables = {}
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
            if table_name in self.tables:
                self.tables[table_name] = pl.concat([
                    self.tables[table_name], df
                ])
            else:
                self.tables[table_name] = df
        
    psql = MockPSQL()
    mocker.patch("src.db.postgresql.PostgreSQL", return_value=psql)
    mocker.patch("src.process.patient_processor.PostgreSQL", return_value=psql)
    mocker.patch("src.process.encounter_processor.PostgreSQL", return_value=psql)
    mocker.patch("src.process.observation_processor.PostgreSQL", return_value=psql)

    return psql

@pytest.fixture
def mock_folder(mocker):
    mocker.patch.dict(os.environ, {
        "BUCKET": "test_bucket",
    })
    folder = Path("test_bucket")
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True, exist_ok=True)
    yield folder
    shutil.rmtree(folder)

@pytest.mark.parametrize("pass_in_folder", [True, False])
def test_main(mock_folder, mock_mongo, mock_sql, pass_in_folder):
    file_path = Path("tests/fixtures/bundle_transaction.json")
    if pass_in_folder:
        main(file_path.parent)
    else:
        main(file_path)

    today_date = datetime.today().strftime("%Y-%m-%d")
    inner_folder = mock_folder / f"upload_date={today_date}"
    assert inner_folder.is_dir() and inner_folder.exists()
    expected_pattern = f"bundle_transaction_{today_date}T*.json"
    found_files = list(mock_folder.rglob(expected_pattern))
    assert len(found_files) == 1

    assert set(mock_mongo.databases.keys()) == set(["test"])
    mongo_test_db = mock_mongo.databases["test"]
    assert set(mongo_test_db.collections.keys()) == set([
        "Patient", "Encounter", "Observation",
        "Condition", "Provenance", "IDReference"
    ])
    assert len(mongo_test_db.collections["Patient"].values) == 1
    assert len(mongo_test_db.collections["Encounter"].values) == 1
    assert len(mongo_test_db.collections["Observation"].values) == 1
    assert len(mongo_test_db.collections["Condition"].values) == 1
    assert len(mongo_test_db.collections["Provenance"].values) == 1
    assert len(mongo_test_db.collections["IDReference"].values) == 5

    assert set(mock_sql.tables.keys()) == set([
        "patient", "encounter", "observation",
    ])
    assert len(mock_sql.tables["patient"]) == 1
    assert len(mock_sql.tables["encounter"]) == 1
    assert len(mock_sql.tables["observation"]) == 1