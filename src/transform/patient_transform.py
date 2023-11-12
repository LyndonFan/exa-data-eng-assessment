import orjson
from typing import Any

from fhir.resources.R4B.patient import Patient

from .base_transform import BaseTransform


class PatientTransform(BaseTransform):
    def transform(self, resource: Patient) -> dict[str, Any]:
        dct = orjson.loads(resource.json(exclude_comments=True, return_bytes=True))
        for unneeded_field in [
            "active",
            "gender",
            "deceasedBoolean",
            "deceasedDateTime",
        ]:
            dct.pop(unneeded_field, None)
        return dct
