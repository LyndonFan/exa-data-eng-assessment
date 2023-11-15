import decimal
import json
import polars as pl
from fhir.resources.R4B.observation import Observation

from src.db.postgresql import PostgreSQL

from src.process.base_processor import BaseProcessor
from src.process.processor_factory import ProcessorFactory


@ProcessorFactory.register("Observation")
class ObservationProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.sql_db = PostgreSQL()

    def process(self, data: list[Observation]):
        super().process(data)
        self.save_to_sql(data)

    def _nested_replace_decimal(self, d):
        # convert from decimal to float as polars can't decode it
        # note this does lose some precision which may be problematic
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, decimal.Decimal):
                    d[k] = float(v)
                else:
                    d[k] = self._nested_replace_decimal(v)
        elif isinstance(d, list):
            for i, v in enumerate(d):
                if isinstance(v, decimal.Decimal):
                    d[i] = float(v)
                else:
                    d[i] = self._nested_replace_decimal(v)
        return d

    def process_data_into_frame(self, data: list[Observation]) -> pl.DataFrame:
        dcts = [e.dict() for e in data]
        FIELDS = [
            "id",
            "code",
            "status",
            "subject",
            "encounter",
            "category",
            "effectiveDateTime",
            "issued",
            "valueQuantity",
            "valueCodeableConcept",
            "component",
        ]
        dcts = [{field: d.get(field) for field in FIELDS} for d in dcts]

        for d in dcts:
            components = []
            if d.get("component"):
                d["component"] = self._nested_replace_decimal(d["component"])
                components.extend(d.pop("component"))
            if d.get("valueQuantity"):
                d["valueQuantity"] = self._nested_replace_decimal(d["valueQuantity"])
                components.append(
                    {
                        "code": d["code"],
                        "valueQuantity": d["valueQuantity"],
                    }
                )
            d.pop("valueQuantity")
            if d.get("valueCodeableConcept"):
                d["valueCodeableConcept"] = self._nested_replace_decimal(
                    d["valueCodeableConcept"]
                )
                components.append(
                    {
                        "code": d["code"],
                        "valueCodeableConcept": d["valueCodeableConcept"],
                    }
                )
            d.pop("valueCodeableConcept")
            d["component"] = json.dumps(components)

        df = pl.DataFrame(dcts)
        df = df.with_columns(
            [
                pl.col("code")
                .struct.field("coding")
                .list.get(0)
                .struct.field("display")
                .alias("observation_type"),
                pl.col("category")
                .list.get(0)
                .struct.field("coding")
                .list.get(0)
                .struct.field("display")
                .alias("category"),
                (
                    pl.col("subject")
                    .struct.field("reference")
                    .str.strip_prefix("urn:uuid:")
                ).alias("patient_id"),
                (
                    pl.col("encounter")
                    .struct.field("reference")
                    .str.strip_prefix("urn:uuid:")
                ).alias("encounter_id"),
            ]
        )
        df = df.drop(["code", "subject", "encounter", "valueCodeableConcept", "valueQuantity"]).rename(
            {
                "effectiveDateTime": "effective_datetime",
                "component": "values",
            }
        )
        return df

    def save_to_sql(self, data: list[Observation]) -> None:
        print(f"Start processing {len(data)} observations into sql")
        df = self.process_data_into_frame(data)
        print("Start uploading to sql for observations")
        self.sql_db.copy_into_table(
            table_name="observation", df=df, json_columns=["values"]
        )
