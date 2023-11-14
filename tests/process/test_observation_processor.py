import json
from decimal import Decimal
import polars as pl
from polars.testing import assert_frame_equal
import pytest
from datetime import datetime

from fhir.resources.R4B.observation import Observation
from src.process.observation_processor import ObservationProcessor


@pytest.fixture
def mock_mongo(mocker):
    mock_mongo = mocker.Mock()
    mocker.patch("src.process.base_processor.Mongo", return_value=mock_mongo)
    yield mock_mongo


@pytest.fixture
def mock_sql(mocker):
    mock_sql = mocker.Mock()
    mocker.patch("src.process.observation_processor.PostgreSQL", return_value=mock_sql)
    yield mock_sql


@pytest.fixture
def processor(mock_mongo, mock_sql):
    processor = ObservationProcessor()
    yield processor


def test_nested_replace_decimal(processor):
    dct = {
        "field_str": "bar",
        "field_decimal": Decimal("1.234"),
        "field_list": [
            Decimal("5.6"),
            {
                "field_str": "foo",
                "field_decimal": Decimal("7.8"),
            },
        ],
    }
    expected_dct = {
        "field_str": "bar",
        "field_decimal": 1.234,
        "field_list": [
            5.6,
            {
                "field_str": "foo",
                "field_decimal": 7.8,
            },
        ],
    }
    assert processor._nested_replace_decimal(dct) == expected_dct


@pytest.fixture
def observations():
    observations = [
        Observation(
            id="1",
            code={"coding": [{"display": "Height"}]},
            status="final",
            subject={"reference": "urn:uuid:123"},
            encounter={"reference": "urn:uuid:456"},
            category=[{"coding": [{"display": "Vital Signs"}]}],
            effectiveDateTime=datetime(2022, 1, 1),
            issued=datetime(2022, 1, 2),
            valueQuantity={"value": Decimal("120"), "unit": "cm"},
            valueCodeableConcept=None,
            component=None,
        ),
        Observation(
            id="2",
            code={"coding": [{"display": "Temperature"}]},
            status="final",
            subject={"reference": "urn:uuid:789"},
            encounter={"reference": "urn:uuid:012"},
            category=[{"coding": [{"display": "Vital Signs"}]}],
            effectiveDateTime=datetime(2022, 1, 3),
            issued=datetime(2022, 1, 4),
            valueQuantity=None,
            valueCodeableConcept={"coding": [{"display": "Fever"}]},
            component=None,
        ),
        Observation(
            id="3",
            code={"coding": [{"display": "Blood Pressure"}]},
            status="final",
            subject={"reference": "urn:uuid:789"},
            encounter={"reference": "urn:uuid:012"},
            category=[{"coding": [{"display": "Vital Signs"}]}],
            effectiveDateTime=datetime(2022, 1, 3),
            issued=datetime(2022, 1, 4),
            valueQuantity=None,
            valueCodeableConcept=None,
            component=[
                {
                    "code": {"coding": [{"display": "Systolic Blood Pressure"}]},
                    "valueQuantity": {"value": Decimal("120")},
                },
                {
                    "code": {"coding": [{"display": "Diastolic Blood Pressure"}]},
                    "valueQuantity": {"value": Decimal("80")},
                },
            ],
        ),
    ]
    return observations


@pytest.fixture
def expected_df():
    values = {
        "id": ["1", "2", "3"],
        "observation_type": ["Height", "Temperature", "Blood Pressure"],
        "status": ["final", "final", "final"],
        "patient_id": ["123", "789", "789"],
        "encounter_id": ["456", "012", "012"],
        "category": ["Vital Signs", "Vital Signs", "Vital Signs"],
        "effective_datetime": [
            datetime(2022, 1, 1),
            datetime(2022, 1, 3),
            datetime(2022, 1, 3),
        ],
        "issued": [
            datetime(2022, 1, 2),
            datetime(2022, 1, 4),
            datetime(2022, 1, 4),
        ],
        "values": [
            json.dumps(
                [
                    {
                        "code": {"coding": [{"display": "Height"}]},
                        "valueQuantity": {"value": 120.0, "unit": "cm"},
                    }
                ]
            ),
            json.dumps(
                [
                    {
                        "code": {"coding": [{"display": "Temperature"}]},
                        "valueCodeableConcept": {"coding": [{"display": "Fever"}]},
                    }
                ]
            ),
            json.dumps(
                [
                    {
                        "code": {"coding": [{"display": "Systolic Blood Pressure"}]},
                        "valueQuantity": {"value": 120.0},
                    },
                    {
                        "code": {"coding": [{"display": "Diastolic Blood Pressure"}]},
                        "valueQuantity": {"value": 80.0},
                    },
                ]
            ),
        ],
    }
    return pl.DataFrame(values)


def test_process_data_into_frame_type_columns(processor, observations):
    result = processor.process_data_into_frame(observations)
    assert isinstance(result, pl.DataFrame)
    expected_columns = [
        "id",
        "observation_type",
        "status",
        "patient_id",
        "encounter_id",
        "category",
        "effective_datetime",
        "issued",
        "values",
    ]
    assert set(result.columns) == set(expected_columns)


def test_process_data_into_frame_correct_value(processor, observations, expected_df):
    result = processor.process_data_into_frame(observations)
    assert_frame_equal(
        result, expected_df, check_column_order=False, check_row_order=False
    )
