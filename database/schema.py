from sqlalchemy import Column, String, Boolean, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Patient(Base):
    __tablename__ = "patient"

    id = Column(String, primary_key=True)
    active = Column(Boolean)
    gender = Column(String)
    birthDate = Column(Date)
    deceasedBoolean = Column(Boolean)
    deceasedDateTime = Column(DateTime)
    name = Column(String)
