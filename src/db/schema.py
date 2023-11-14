import os
from dotenv import load_dotenv
from typing import Optional

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Date, DateTime, JSON
from sqlalchemy.engine import create_engine

from src.db.postgresql import PostgreSQL

load_dotenv()


class Base(DeclarativeBase):
    pass


class Patient(Base):
    __tablename__ = "patient"

    id: Mapped[str] = mapped_column(primary_key=True)
    active: Mapped[Optional[bool]]
    name: Mapped[Optional[str]]
    maiden_name: Mapped[Optional[str]]
    gender: Mapped[Optional[str]]
    birth_date = mapped_column(Date, nullable=True)
    deceased: Mapped[Optional[bool]]
    deceased_datetime = mapped_column(DateTime, nullable=True)
    marital_status: Mapped[Optional[str]]

    encounters: Mapped[list["Encounter"]] = relationship(back_populates="patient")
    observations: Mapped[list["Observation"]] = relationship(back_populates="patient")


class Encounter(Base):
    __tablename__ = "encounter"

    id: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[str]
    patient: Mapped[Patient] = relationship(back_populates="encounters")
    patient_id: Mapped[str] = mapped_column(ForeignKey("patient.id"))
    class_code: Mapped[Optional[str]]
    period_start = mapped_column(DateTime, nullable=True)
    period_end = mapped_column(DateTime, nullable=True)
    reason: Mapped[Optional[str]]
    location: Mapped[Optional[str]]

    observations: Mapped[list["Observation"]] = relationship(back_populates="encounter")


class Observtaion(Base):
    __tablename__ = "observation"

    id: Mapped[str] = mapped_column(primary_key=True)
    observation_type: Mapped[str]
    status: Mapped[str]
    patient: Mapped[Patient] = relationship(back_populates="observations")
    patient_id: Mapped[str]
    encounter: Mapped[Encounter] = relationship(back_populates="observations")
    encounter_id: Mapped[str]
    category: Mapped[Optional[str]]
    effective_datetime = mapped_column(DateTime, nullable=True)
    issued = mapped_column(DateTime, nullable=True)
    values = mapped_column(JSON)


def create_all_tables():
    db = PostgreSQL()
    engine_string = os.environ["PSQL_URI"].split("://")[0]
    engine = create_engine(engine_string + "://", creator=db.connection, echo=True)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_all_tables()
