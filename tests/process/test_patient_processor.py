import pytest
from datetime import datetime
import polars as pl
from polars.testing import assert_frame_equal
from fhir.resources.R4B.patient import Patient

from src.process.patient_processor import PatientProcessor

@pytest.fixture
def mock_mongo(mocker):
    mock_mongo = mocker.Mock()
    mocker.patch("src.process.base_processor.Mongo", return_value=mock_mongo)
    yield mock_mongo

@pytest.fixture
def mock_sql(mocker):
    mock_sql = mocker.Mock()
    mocker.patch("src.process.patient_processor.PostgreSQL", return_value=mock_sql)
    yield mock_sql

@pytest.fixture
def processor(mock_mongo, mock_sql):
    return PatientProcessor()

@pytest.fixture
def expected_df():
    # Generate expected DataFrame
    values = {
        "id": ["1", "2", "3", "4"],
        "active": [True, True, False, False],
        "gender": ["male", "female", "other", "unknown"],
        "birth_date": [
            datetime(1990, 1, 1).date(),
            datetime(1995, 12, 16).date(),
            datetime(2000, 12, 16).date(),
            None,
        ],
        "name": [
            "John Doe",
            "Jane Smith",
            "Marshall",
            None,
        ],
        "maiden_name": [
            None,
            "Jane White",
            None,
            None,
        ],
        "deceased": [False, False, True, True],
        "deceased_datetime": [
            None,
            None,
            datetime(2022, 10, 6),
            None,
        ],
        "marital_status": [
            "M",
            "M",
            "S",
            "UNK",
        ]
    }
    df = pl.DataFrame(values)
    return df

def test_process_data_into_frame_correct_values(processor, patients, expected_df):
    result = processor.process_data_into_frame(patients)
    assert_frame_equal(
        result, expected_df, check_column_order=False, check_row_order=False
    )