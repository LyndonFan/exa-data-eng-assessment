import pytest
import orjson
from datetime import datetime
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
def patients():
    return [
        Patient(
            id="1",
            active=True,
            name=[
                {
                    "use": "official",
                    "family": "Doe",
                    "given": ["John"],
                    "text": "John Doe",
                }
            ],
            gender="male",
            birthDate=datetime(1990, 1, 1),
            deceasedBoolean=False,
            maritalStatus={
                "text": "M",
            },
        ),
        Patient(
            id="2",
            active=True,
            name=[
                {
                    "use": "official",
                    "family": "Smith",
                    "given": ["Jane"],
                },
                {
                    "use": "maiden",
                    "family": "White",
                    "given": ["Jane"],
                },
            ],
            gender="female",
            birthDate=datetime(1995, 12, 16),
            deceasedBoolean=False,
            maritalStatus={
                "text": "M",
            },
        ),
    ]

@pytest.fixture
def patient_dict(patients):
    dcts = [orjson.loads(orjson.dumps(patient.dict())) for patient in patients]
    for dct in dcts:
        dct["_id"] = dct.pop("id")
        dct.pop("resourceType")
    return dcts

@pytest.fixture
def encounters():
    return [
        Encounter(
            id="1",
            status="final",
            subject={"reference": "urn:uuid:123"},
            class_fhir={"code": "IMP"},
            period={"start": datetime(2022, 1, 1), "end": datetime(2022, 1, 2)},
            location=[
                {
                    "location": {
                        "reference": "Location?MadeUp",
                        "display": "MadeUp Location",
                    }
                }
            ],
            reasonCode=[
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "123",
                            "display": "MadeUp Reason",
                        }
                    ]
                }
            ],
        ),
    ]

@pytest.fixture
def encounter_dict(encounters):
    dcts = [orjson.loads(orjson.dumps(encounter.dict())) for encounter in encounters]
    for dct in dcts:
        dct["_id"] = dct.pop("id")
        dct.pop("resourceType")
    return dcts

@pytest.fixture
def observations():
    return [
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
    ]

@pytest.fixture
def observation_dict(observations):
    dcts = [orjson.loads(orjson.dumps(observation.dict())) for observation in observations]
    for dct in dcts:
        dct["_id"] = dct.pop("id")
        dct.pop("resourceType")
    return dcts

@pytest.fixture
def provenances():
    return [
        Provenance(
            id="1",
            recorded=datetime(2022, 1, 1, 12, 0, 0),
            agent=[{"who":{"reference": "urn:uuid:123"}}],
            target=[
                {"reference": "urn:uuid:123"},
                {"reference": "urn:uuid:456"},
                {"reference": "urn:uuid:789"},
                {"reference": "urn:uuid:012"},
            ],
        ),
    ]

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