
import pytest
from src.process.base_processor import BaseProcessor
from src.process.processor_factory import ProcessorFactory
from fhir.resources.R4B.resource import Resource

@pytest.fixture(autouse=True)
def reset():
    old_registry = {**ProcessorFactory._registry}
    ProcessorFactory._registry = {}
    yield
    ProcessorFactory._registry = old_registry

def test_register_processor_class():
    @ProcessorFactory.register("TestResource")
    class TestProcessor(BaseProcessor):
        pass

    assert "TestResource" in ProcessorFactory._registry
    assert ProcessorFactory._registry["TestResource"] == TestProcessor

def test_register_existing_resource_type():
    @ProcessorFactory.register("TestResource")
    class TestProcessor(BaseProcessor):
        pass

    with pytest.raises(ValueError):
        @ProcessorFactory.register("TestResource")
        class TestProcessor2(BaseProcessor):
            pass

def test_process_single_type(patients):
    called = []
    @ProcessorFactory.register("Patient")
    class TestProcessor(BaseProcessor):
        def process(self, data):
            called.append([d.id for d in data])

    ProcessorFactory.process_single_type(patients)
    assert called == [["1", "2", "3", "4"]]
    
# TODO: Fix this
# commenting out instead of marking as skip
# as too many combinations
# @pytest.mark.parametrize("has_patient", [True, False])
# @pytest.mark.parametrize("has_encounter", [True, False])
# @pytest.mark.parametrize("has_observation", [True, False])
# @pytest.mark.parametrize("has_other", [True, False])
# def test_batch_process(
#     patients, has_patient,
#     encounters, has_encounter,
#     observations, has_observation,
#     provenances, has_other,
#     mocker
# ):
    
#     expected_call_order = []
#     if has_patient:
#         expected_call_order.append("Patient")
#     if has_encounter:
#         expected_call_order.append("Encounter")
#     if has_observation:
#         expected_call_order.append("Observation")
#     if has_other:
#         expected_call_order.append("Other")
    
#     actual_call_order = []

#     def mock_process_patient(data):
#         actual_call_order.append("Patient")
    
#     def mock_process_encounter(data):
#         actual_call_order.append("Encounter")
    
#     def mock_process_observation(data):
#         actual_call_order.append("Observation")
    
#     def mock_process_other(data):
#         actual_call_order.append("Other")
    
#     mocker.patch("src.process.processor_factory.BaseProcessor.process", side_effect=mock_process_other)
#     mocker.patch("src.process.patient_processor.PatientProcessor.process", side_effect=mock_process_patient)
#     mocker.patch("src.process.encounter_processor.EncounterProcessor.process", side_effect=mock_process_encounter)
#     mocker.patch("src.process.observation_processor.ObservationProcessor.process", side_effect=mock_process_observation)


#     # @ProcessorFactory.register("Patient")
#     # class TestPatientProcessor(BaseProcessor):
#     #     def process(self, data):
#     #         actual_call_order.append("Patient")
#     #      
    
#     # @ProcessorFactory.register("Encounter")
#     # class TestEncounterProcessor(BaseProcessor):
#     #     def process(self, data):
#     #         actual_call_order.append("Encounter")
#     #      
    
#     # @ProcessorFactory.register("Observation")
#     # class TestObservationProcessor(BaseProcessor):
#     #     def process(self, data):
#     #         actual_call_order.append("Observation")
#     #      
    
#     data = []
#     if has_patient:
#         data.extend(patients)
#     if has_encounter:
#         data.extend(encounters)
#     if has_observation:
#         data.extend(observations)
#     if has_other:
#         data.extend(provenances)
    
#     data.reverse()

#     ProcessorFactory.batch_process(data)

#     assert actual_call_order == expected_call_order