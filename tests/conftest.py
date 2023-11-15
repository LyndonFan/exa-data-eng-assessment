import pytest

@pytest.fixture(autouse=True)
def no_actual_mongo(mocker):
    mocker.patch("pymongo.MongoClient")

@pytest.fixture(autouse=True)
def no_actual_sql(mocker):
    mocker.patch("psycopg2.connect")
    mocker.patch("sqlalchemy.create_engine")
    mocker.patch("pandas.DataFrame.to_sql", return_value=None)
    mocker.patch("polars.DataFrame.write_database", return_value=None)