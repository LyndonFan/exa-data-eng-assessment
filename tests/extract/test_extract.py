import pytest

from fhir.resources.R4B.bundle import Bundle

from src.extract.extract import Extractor

def test_extract():
    transaction_bundle_path = "tests/fixtures/bundle_transaction.json"
    bundle = Bundle.parse_file("tests/fixtures/bundle_transaction.json")
    expected = [e.resource for e in bundle.entry]
    actual = Extractor().extract(transaction_bundle_path)
    assert expected == actual

@pytest.mark.xfail
def test_extract_not_bundle():
    patient_bundle_path = "tests/fixtures/patient.json"
    _ = Extractor().extract(patient_bundle_path)
