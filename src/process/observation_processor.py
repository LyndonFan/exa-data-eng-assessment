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

    def process_data_into_frame(self, data: list[Observation]) -> pl.DataFrame:
        dcts = [e.dict() for e in data]
        FIELDS = [
            "id",
            "code",
            "subject",
            "encounter",
            "category",
            "effectiveDateTime",
            "issued",
            "valueQuantity",
            "valueCodeableConcept",
            "component",
        ]
        dcts = [{f: d.get(f) for f in FIELDS} for d in dcts]
        VALUE_COLUMNS = [
            "valueQuantity",
            "valueCodeableConcept",
            "component",
        ]
        for d in dcts:
            for c in VALUE_COLUMNS:
                if d.get(c) is not None:
                    d[c] = json.dumps(d[c])
        
        df = pl.DataFrame(dcts)
        df = df.with_columns(
            [
                pl.col("code")
                .struct.field('coding')
                .list.get(0)
                .struct.field('display')
                .alias("observation_type"),
                pl.col("category")
                .list.get(0)
                .struct.field('coding')
                .list.get(0)
                .struct.field('display')
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
        df = df.with_columns(pl.coalesce(
            pl.when(pl.col("valueQuantity").is_null).then(pl.lit(None)).otherwise("[" + pl.col("valueQuantity") + "]"),
            pl.when(pl.col("valueCodeableConcept").is_null).then(pl.lit(None)).otherwise("[" + pl.col("valueCodeableConcept") + "]"),
            pl.col("component"),
        ).alias("values"))
        df = df.drop(["code", "subject"] + VALUE_COLUMNS).rename(
            {
                "effectiveDateTime": "effective_datetime",
                "component": "values",
            }
        )
        return df

    def save_to_sql(self, data: list[Observation]) -> None:
        print(f"Start processing {len(data)} observations into sql")
        df = self.process_data_into_frame(data)
        print(f"Start uploading to sql for observations")
        self.sql_db.copy_into_table(table_name="observation", df=df, json_columns=["values"])
