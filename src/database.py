from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True, nullable=False)


class Identifier(Base):
    __tablename__ = 'identifiers'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    identifier = Column(String, nullable=False)
    identifier_type = Column(String, nullable=False)


class OutageData(Base):
    __tablename__ = 'outage_data'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    identifier = Column(String, nullable=False)
    identifier_type = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_seconds = Column(Float, nullable=False)


def init_db():
    Base.metadata.create_all(engine)
