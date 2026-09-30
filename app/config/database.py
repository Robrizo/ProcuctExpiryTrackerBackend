import os
from typing import Annotated
from urllib.parse import quote_plus

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

password = quote_plus(os.getenv("DATABASE_PASSWORD"))
username = os.getenv("DATABASE_USER")
host = os.getenv("DATABASE_HOST")
port = os.getenv("DATABASE_PORT")
name = os.getenv("DATABASE_NAME")

DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]