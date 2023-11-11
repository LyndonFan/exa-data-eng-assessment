import orjson
from typing import Any

from fhir.resources.R4B.resource import Resource

from .base_transform import BaseTransform
from .transform_factory import TransformFactory

@TransformFactory.register("Default")
class DefaultTransform(BaseTransform):
    def transform(self, resource: Resource) -> dict[str, Any]:
        dct = orjson.loads(resource.json(exclude_comments=True, return_bytes=True))

        return dct
