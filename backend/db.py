from sqlalchemy import create_engine, URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = URL.create(
  'postgresql',
  username = os.getenv('PGUSER'),
  password = os.getenv('PGPASSWORD'),
  host = os.getenv('PGHOST'),
  database = os.getenv('PGDATABASE'),
  # connect_args={'sslmode':'require'}
)
# SQLALCHEMY_DATABASE_URL = "sqlite:///../db/soccer.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()