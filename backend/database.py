"""
Phase 5 -- Database connection/session setup (PostgreSQL).

Uses SQLAlchemy's engine + session pattern. Connection string is read
from an environment variable so you're not hardcoding credentials.

Set this env var before running anything that touches the DB:
    DATABASE_URL=postgresql://user:password@localhost:5432/shelf_monitoring

(For Railway/Render deployment later, they'll each give you a connection
string in this same format -- just swap the env var value.)
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/shelf_monitoring",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency -- yields a DB session and always closes it
    afterward, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()