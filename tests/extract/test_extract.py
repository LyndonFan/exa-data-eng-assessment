import pytest

from fhir.resources.R4B.bundle import Bundle

from src.extract.extract import Extractor


class TestExtractor:
    def test_extract(self):
        transaction_bundle_path = "tests/fixtures/bundle_transaction.json"
        bundle = Bundle.parse_file("tests/fixtures/bundle_transaction.json")
        expected_entries = bundle.entry
        actual_entries = Extractor().extract(transaction_bundle_path)
        assert expected_entries == actual_entries

    @pytest.mark.xfail
    def test_extract_not_bundle(self):
        patient_bundle_path = "tests/fixtures/patient.json"
        _ = Extractor().extract(patient_bundle_path)
