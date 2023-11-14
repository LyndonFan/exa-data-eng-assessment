from typing import Optional
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.humanname import HumanName
import polars as pl

from src.db.postgresql import PostgreSQL

from src.process.base_processor import BaseProcessor
from src.process.processor_factory import ProcessorFactory


@ProcessorFactory.register("Patient")
class PatientProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.sql_db = PostgreSQL()

    def process(self, data: list[Patient]):
        super().process(data)
        self.save_to_sql(data)

    def _infer_name(self, name: HumanName) -> Optional[str]:
        if name.text is not None:
            return name.text
        # below assumes a "western" name
        # likely breaks on non-western names and/or missing/multiple values
        if not name.given:
            return None
        if name.family:
            return f"{name.given[0]} {name.family}"
        return name.given[0]

    def process_data_into_frame(self, data: list[Patient]) -> pl.DataFrame:
        res = []

        # Unable to simply convert to pl.DataFrame
        # runs into a ComputeError
        for patient in data:
            dct = {
                "id": patient.id,
                "active": patient.active,
                "gender": patient.gender,
                "birth_date": patient.birthDate,
                "deceased": patient.deceasedBoolean,
                "deceased_datetime": patient.deceasedDateTime,
                "martial_status": patient.maritalStatus,
            }

            # as per comment in below link,
            # assume default of person not deceased
            # https://hl7.org/fhir/R4B/patient-definitions.html#Patient.deceased_x_
            if not dct["deceased"]:
                dct["deceased"] = dct["deceased_datetime"] is not None

            if dct["martial_status"] is not None:
                dct["martial_status"] = dct["martial_status"].text

            dct["name"] = None
            dct["maiden_name"] = None
            for name in patient.name:
                if name.use == "official":
                    dct["name"] = self._infer_name(name)
                elif name.use == "maiden":
                    dct["maiden_name"] = self._infer_name(name)
            res.append(dct)

        return pl.DataFrame(res)

    def save_to_sql(self, data: list[Patient]) -> None:
        print(f"Start processing {len(data)} patients into sql")
        df = self.process_data_into_frame(data)
        print("Start uploading to sql for patients")
        self.sql_db.copy_into_table(table_name="patient", df=df)
