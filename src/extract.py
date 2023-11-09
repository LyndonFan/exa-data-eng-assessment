from pathlib import Path
from fhir.resources.R4B.bundle import Bundle, BundleEntry

class Extractor:
    def __init__(self):
        pass

    def extract(self, payload_path: str | Path) -> list[BundleEntry]:
        bundle = Bundle.parse_file(payload_path)
        if bundle.type != "transaction":
            raise ValueError(f"Expected transaction bundle, got {bundle.type}")
        if bundle.entry is None:
            raise ValueError(f"Expected bundle entry, got {bundle.entry}")
        return bundle.entry # type: ignore