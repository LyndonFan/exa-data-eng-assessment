from typing import Type, Any
from fhir.resources.R4B.resource import Resource
from src.transform.base_transform import BaseTransform


class TransformFactory:
    _registry: dict[str, Type[BaseTransform]] = {}

    @classmethod
    def register(cls, resource_type: str):
        """
        Register which resource_type the transformation is designed for

        Args:
            name (str): the transformation name
        """

        def wrapper(subcls: Type[BaseTransform]) -> Type[BaseTransform]:
            if resource_type in cls._registry:
                raise ValueError(f"Transform {resource_type} already registered")
            cls._registry[resource_type] = subcls
            return subcls

        return wrapper

    @classmethod
    def transform(cls, resource: Resource) -> dict[str, Any]:
        resource_type = resource.resource_type
        if resource_type not in cls._registry:
            resource_type = "Default"
        corr_transformer = cls._registry[resource_type]
        return corr_transformer().transform(resource)
