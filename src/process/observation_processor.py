import decimal
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
                    self._nested_replace_decimal(v)
        elif isinstance(d, list):
            for i in d:
                self._nested_replace_decimal(i)

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
        self._nested_replace_decimal(dcts)
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
        df = df.drop(["code", "subject"]).rename(
            {
                "effectiveDateTime": "effective_datetime",
                "component": "values",
            }
        )
        return df

    def save_to_sql(self, data: list[Observation]) -> None:
        df = self.process_data_into_frame(data)
        self.sql_db.copy_into_table(table_name="observation", df=df, json_columns=["values"])
