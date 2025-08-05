from pymongo import MongoClient
from app.core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeBase

Base: DeclarativeBase = declarative_base()
engine = create_engine(settings.active_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mongo_db():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_INITDB_DATABASE]
    return db