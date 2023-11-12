from typing import Optional
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.humanname import HumanName

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

    def reformat_data_for_sql(self, data: list[Patient]) -> list[dict]:
        res = []
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
        return res

    def save_to_sql(self, data: list[Patient]) -> None:
        reformatted_data = self.reformat_data_for_sql(data)
        with self.sql_db.connection() as conn:
            with conn.cursor() as cursor:
                insert_statement = """
                    INSERT INTO patient
                    (id, active, gender, birth_date, deceased, deceased_datetime, martial_status, name, maiden_name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET 
                        active = EXCLUDED.active,
                        gender = EXCLUDED.gender,
                        birth_date = EXCLUDED.birth_date,
                        deceased = EXCLUDED.deceased,
                        deceased_datetime = EXCLUDED.deceased_datetime,
                        martial_status = EXCLUDED.martial_status,
                        name = EXCLUDED.name,
                        maiden_name = EXCLUDED.maiden_name
                """

                execute_data = [
                    (
                        row["id"],
                        row["active"],
                        row["gender"],
                        row["birth_date"],
                        row["deceased"],
                        row["deceased_datetime"],
                        row["martial_status"],
                        row["name"],
                        row["maiden_name"],
                    )
                    for row in reformatted_data
                ]

                cursor.executemany(insert_statement, execute_data)
                conn.commit()
