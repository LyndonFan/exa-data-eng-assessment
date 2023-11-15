import pytest

@pytest.fixture(autouse=True)
def no_actual_mongo(mocker):
    mocker.patch("pymongo.MongoClient")

@pytest.fixture(autouse=True)
def no_actual_sql(mocker):
    mocker.patch("psycopg2.connect")
    mocker.patch("sqlalchemy.create_engine")