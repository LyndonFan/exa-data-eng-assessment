from typing import Optional
import polars as pl
from fhir.resource.R4B.observation import Observation

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
        """

    id: Mapped[str] = mapped_column(primary_key=True)
    code: Mapped[str]
    patient: Mapped[Patient] = relationship(back_populates="observations")
    patient_id: Mapped[str]
    encounter: Mapped[Encounter] = relationship(back_populates="observations")
    encounter_id: Mapped[str]
    category: Mapped[Optional[str]]
    values: Mapped[Optional[str]]
    effective_datetime = mapped_column(DateTime, nullable=True)
    issued = mapped_column(DateTime, nullable=True)
        """
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
            "component"
        ]
        dcts = [{f: d.get(f) for f in FIELDS} for d in dcts]
        for d in dcts:
            # convert from decimal to float as polars can't decode it
            # note this does lose some precision which may be problematic
            if d["valueQuantity"]:
                d["valueQuantity"]["value"] = float(d["valueQuantity"]["value"])
                d["component"] = [d.pop("valueQuantity")]
            if d["valueCodeableConcept"]:
                d["component"] = [d.pop("valueCodeableConcept")]
        df = polars.DataFrame(dcts)
        df = df.with_columns(
            [
                pl.col("code").coding.list.get(0).display.alias("observation_type"),
                pl.col("category").list.get(0).coding.list.get(0).display.alias("category"),
                (
                    pl.col("subject").struct.field("reference")
                    .str.strip_prefix("urn:uuid:")
                ).alias("patient_id"),
                (
                    pl.col("encounter").struct.field("reference")
                    .str.strip_prefix("urn:uuid:")
                ).alias("encounter_id"),
            ]
        )
        df = df.drop(["code", "subject"]).rename({
            "effectiveDateTime": "effective_datetime",
            "component": "values",
        })
        return df

    def save_to_sql(self, data: list[Patient]) -> None:
        df = self.process_data_into_frame(data)
        self.sql_db.copy_into_table(table_name="observation", df=df)