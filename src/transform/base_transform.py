from abc import ABC
from typing import Any
from fhir.resources.R4B.resource import Resource


class BaseTransform(ABC):
    def __init__(self) -> None:
        pass

    def transform(self, resource: Resource) -> dict[str, Any]:
        raise NotImplementedError
