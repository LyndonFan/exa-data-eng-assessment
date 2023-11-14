from typing import Optional, Type
from fhir.resources.R4B.resource import Resource
from .base_processor import BaseProcessor


class ProcessorFactory:
    _registry = {}

    @classmethod
    def register(cls, resource_type: str):
        def wrapper(processor_cls: Type[BaseProcessor]):
            if resource_type in cls._registry:
                raise ValueError(f"Resource type {resource_type} already registered")
            cls._registry[resource_type] = processor_cls
            return processor_cls

        return wrapper

    @classmethod
    def process_single_type(
        cls, data: list[Resource], resource_type: Optional[str] = None
    ):
        if resource_type is None:
            resource_type = data[0].resource_type
        processor = cls._registry.get(resource_type, BaseProcessor)
        processor().process(data)

    @classmethod
    def batch_process(cls, data: list[Resource]):
        groups = {}
        for i, d in enumerate(data):
            resource_type = d.resource_type
            if resource_type not in groups:
                groups[resource_type] = []
            groups[resource_type].append(i)
        
        # TODO: A sort of clever way to include dependencies
        # and generate order from DAG
        if "Patient" in groups:
            cls.process_single_type([data[i] for i in groups["Patient"]], "Patient")
        if "Encounter" in groups:
            cls.process_single_type([data[i] for i in groups["Encounter"]], "Encounter")
        if "Observation" in groups:
            cls.process_single_type([data[i] for i in groups["Observation"]], "Observation")
        for resource_type, indexes in groups.items():
            if resource_type in ["Patient", "Encounter", "Observation"]:
                continue
            cls.process_single_type([data[i] for i in indexes], resource_type)
