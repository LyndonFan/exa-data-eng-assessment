from datetime import datetime
import polars as pl
from polars.testing import assert_frame_equal
import pytest
from fhir.resources.R4B.encounter import Encounter

from src.process.encounter_processor import EncounterProcessor


@pytest.fixture
def mock_mongo(mocker):
    mock_mongo = mocker.Mock()
    mocker.patch("src.process.base_processor.Mongo", return_value=mock_mongo)
    yield mock_mongo


@pytest.fixture
def mock_sql(mocker):
    mock_sql = mocker.Mock()
    mocker.patch("src.process.encounter_processor.PostgreSQL", return_value=mock_sql)
    yield mock_sql


@pytest.fixture
def processor(mock_mongo, mock_sql):
    processor = EncounterProcessor()
    yield processor

@pytest.fixture
def expected_df():
    values = {
        "id": ["1", "2"],
        "status": ["final", "cancelled"],
        "patient_id": ["123", "456"],
        "class_code": ["IMP", "IMP"],
        "period_start": [datetime(2022, 1, 1), datetime(2022, 4, 1)],
        "period_end": [datetime(2022, 1, 2), datetime(2022, 4, 2)],
        "location": ["MadeUp Location", "Another One"],
        "reason": ["MadeUp Reason", "Another Reason"],
    }
    df = pl.DataFrame(values)
    return df

def test_process_data_into_frame_correct_values(processor, encounters, expected_df):
    result = processor.process_data_into_frame(encounters)
    assert_frame_equal(
        result, expected_df, check_column_order=False, check_row_order=False
    )