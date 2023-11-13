from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Date, DateTime


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
    martial_status: Mapped[Optional[str]]


if __name__ == "__main__":
    from src.db.postgresql import PostgreSQL
    from sqlalchemy.engine import create_engine

    db = PostgreSQL()
    engine = create_engine("cockroachdb://", creator=db.connection, echo=True)
    Base.metadata.create_all(engine)
