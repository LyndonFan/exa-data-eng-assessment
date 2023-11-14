import pytest
import orjson
from datetime import datetime
from decimal import Decimal
from fhir.resources.R4B.provenance import Provenance
from fhir.resources.R4B.encounter import Encounter
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.observation import Observation

from src.process.base_processor import BaseProcessor

@pytest.fixture
def mock_mongo(mocker):
    mock_mongo = mocker.Mock()
    mocker.patch("src.process.base_processor.Mongo", return_value=mock_mongo)
    yield mock_mongo

@pytest.fixture
def processsor(mock_mongo):
    return BaseProcessor()

@pytest.fixture
def patient_dict(patients):
    dcts = [orjson.loads(orjson.dumps(patient.dict())) for patient in patients]
    for dct in dcts:
        dct["_id"] = dct.pop("id")
        dct.pop("resourceType")
    return dcts

@pytest.fixture
def encounter_dict(encounters):
    dcts = [orjson.loads(orjson.dumps(encounter.dict())) for encounter in encounters]
    for dct in dcts:
        dct["_id"] = dct.pop("id")
        dct.pop("resourceType")
    return dcts

@pytest.fixture
def observation_dict(observations):
    def default_decimal(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError

    dcts = [orjson.loads(orjson.dumps(observation.dict(), default=default_decimal)) for observation in observations]
    for dct in dcts:
        dct["_id"] = dct.pop("id")
        dct.pop("resourceType")
    return dcts


@pytest.fixture
def provenance_dict(provenances):
    dcts = [orjson.loads(orjson.dumps(provenance.dict())) for provenance in provenances]
    for dct in dcts:
        dct["_id"] = dct.pop("id")
        dct.pop("resourceType")
    return dcts


def test_process_data_for_mongo_patient(patients, patient_dict):
    processor = BaseProcessor()
    resource_type, to_save_data, id_references = processor.process_data_for_mongo(
        patients
    )
    assert resource_type == "Patient"
    assert to_save_data == patient_dict
    assert id_references == [{"_id": d["_id"], "resource_type": "Patient"} for d in patient_dict]

def test_process_data_for_mongo_encounter(encounters, encounter_dict):
    processor = BaseProcessor()
    resource_type, to_save_data, id_references = processor.process_data_for_mongo(
        encounters
    )
    assert resource_type == "Encounter"
    assert to_save_data == encounter_dict
    assert id_references == [{"_id": d["_id"], "resource_type": "Encounter"} for d in encounter_dict]

def test_process_data_for_mongo_observations(observations, observation_dict):
    processor = BaseProcessor()
    resource_type, to_save_data, id_references = processor.process_data_for_mongo(
        observations
    )
    assert resource_type == "Observation"
    assert to_save_data == observation_dict
    assert id_references == [
        {"_id": d["_id"], "resource_type": "Observation"} for d in observation_dict
    ]

def test_process_data_for_mongo_provenances(provenances, provenance_dict):
    processor = BaseProcessor()
    resource_type, to_save_data, id_references = processor.process_data_for_mongo(
        provenances
    )
    assert resource_type == "Provenance"
    assert to_save_data == provenance_dict
    assert id_references == [
        {"_id": d["_id"], "resource_type": "Provenance"} for d in provenance_dict
    ]