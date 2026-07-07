"""
Phase 5 -- Database setup script.

Creates all tables (products, inventory, alerts) in PostgreSQL based
on the models defined in models.py.

Usage:
    python init_db.py

Run this once, after setting DATABASE_URL and creating an empty
PostgreSQL database for the project.
"""

from database import Base, engine
import models  # noqa: F401 -- must be imported so Base knows about the tables


def init_db() -> None:
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created: products, inventory, alerts")


if __name__ == "__main__":
    init_db()