from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, Date, DateTime

class Base(DeclarativeBase):
    pass

class Patient(Base):
    __tablename__ = "patient"

    id: Mapped[str] = mapped_column(primary_key=True)
    active: Mapped[bool] = mapped_column(nullable=False)
    name: Mapped[str]
    maiden_name: Mapped[str]
    gender: Mapped[str]
    birth_date = mapped_column(Date)
    deceased: Mapped[bool]
    decease_datetime = mapped_column(DateTime)
    martial_status: Mapped[str]


if __name__ == "__main__":
    from src.db.postgresql import PostgreSQL
    from sqlalchemy.engine import create_engine

    db = PostgreSQL()
    engine = create_engine("cockroachdb://", creator=db.connection, echo=True)
    Base.metadata.create_all(engine)