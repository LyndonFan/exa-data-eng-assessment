import logging
import polars as pl
from fhir.resources.R4B.encounter import Encounter

from src.db.postgresql import PostgreSQL

from src.process.base_processor import BaseProcessor
from src.process.processor_factory import ProcessorFactory


@ProcessorFactory.register("Encounter")
class EncounterProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.sql_db = PostgreSQL()

    def process(self, data: list[Encounter]):
        super().process(data)
        self.save_to_sql(data)

    def process_data_into_frame(self, data: list[Encounter]) -> pl.DataFrame:
        dcts = [e.dict() for e in data]
        FIELDS = [
            "id",
            "status",
            "class",
            "subject",
            "period",
            "location",
            "reasonCode",
        ]
        dcts = [{field: d.get(field) for field in FIELDS} for d in dcts]
        df = pl.DataFrame(dcts)

        df = df.with_columns(
            [
                pl.col("class").struct.field("code").alias("class_code"),
                (
                    pl.col("subject")
                    .struct.field("reference")
                    .str.strip_prefix("urn:uuid:")
                ).alias("patient_id"),
                pl.col("period").struct.field("start").alias("period_start"),
                pl.col("period").struct.field("end").alias("period_end"),
            ]
        )

        if df["reasonCode"].is_not_null().any():
            df = df.with_columns(
                pl.when(pl.col("reasonCode").is_null())
                .then(pl.lit(None))
                .otherwise(
                    pl.col("reasonCode")
                    .list.get(0)
                    .struct.field("coding")
                    .list.get(0)
                    .struct.field("display")
                )
                .alias("reason")
            )
        else:
            df = df.with_columns(pl.lit(None).cast(pl.Utf8).alias("reason"))
        
        if df["location"].is_not_null().any():
            df = df.with_columns(
                pl.when(pl.col("location").is_null())
                .then(pl.lit(None))
                .otherwise(
                    pl.col("location")
                    .list.get(0)
                    .struct.field("location")
                    .struct.field("display")
                )
                .alias("location")
            )
        else:
            df = df.with_columns(pl.col("location").cast(pl.Utf8))
        
        df = df.drop(["subject", "class", "period", "reasonCode"])
        return df

    def save_to_sql(self, data: list[Encounter]) -> None:
        logging.info(f"Start processing {len(data)} encounters into sql")
        df = self.process_data_into_frame(data)
        logging.info("Start uploading to sql for encounters")
        self.sql_db.copy_into_table(table_name="encounter", df=df)
