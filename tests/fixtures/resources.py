from datetime import datetime
from decimal import Decimal
import pytest

from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.encounter import Encounter
from fhir.resources.R4B.observation import Observation
from fhir.resources.R4B.provenance import Provenance

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
            }
        ),
        Patient(
            id="3",
            active=False,
            name=[
                {
                    "use": "official",
                    "given": ["Marshall"],
                },
            ],
            gender="other",
            birthDate=datetime(2000, 12, 16),
            deceasedDateTime=datetime(2022, 10, 6),
            maritalStatus={
                "text": "S",
            }
        ),
        Patient(
            id="4",
            active=False,
            name=[],
            gender="unknown",
            deceasedBoolean=True,
            maritalStatus={
                "text": "UNK",
            }
        )
    ]

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
        Encounter(
            id="2",
            status="cancelled",
            subject={"reference": "urn:uuid:456"},
            class_fhir={"code": "IMP"},
            period={"start": datetime(2022, 4, 1), "end": datetime(2022, 4, 2)},
            location=[
                {
                    "location": {
                        "reference": "Location?AnotherOne",
                        "display": "Another One",
                    }
                }
            ],
            reasonCode=[
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "789",
                            "display": "Another Reason",
                        }
                    ]
                }
            ],
        )
    ]

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
