from datetime import datetime
from io import StringIO
import pandas as pd
import orjson
from fhir.resources.R4B.patient import Patient

from src.db.mongo import Mongo
from src.db.postgresql import PostgreSQL

from src.process.base_processor import BaseProcessor

class PatientProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.sql_db = PostgreSQL()

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

            for name in patient.name:
                if name.use == "official":
                    dct["name"] = name.text
                elif name.use == "maiden":
                    dct["maiden_name"] = name.text
            res.append(dct)
            
        return res
    
    def save_to_sql(self, data: list[Patient]) -> None:
        reformatted_data = self.reformat_data_for_sql(data)
        df = pd.DataFrame(reformatted_data)
        sio = StringIO()
        df.to_csv(sio, index=False)
        sio.seek(0)
        with self.sql_db.connection() as conn:
            with conn.cursor() as cursor:
                # Create a temporary table to hold the data
                cursor.execute("CREATE TEMPORARY TABLE temp_patient (LIKE patient)")

                cursor.copy_from(
                    sio,
                    "temp_patient",
                    columns=df.columns.tolist(),
                )

                # Perform upsert by merging the temporary table with the patient table
                cursor.execute("""
                    INSERT INTO patient
                    SELECT * FROM temp_patient
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
                """)

                conn.commit()