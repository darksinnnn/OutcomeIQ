"""
Database configuration and session management for CAT OutcomeIQ.
"""

import os
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.db.models import Base

# Locate the database file path
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "data" / "seed"
DB_PATH = DB_DIR / "catiq.db"

# Create sqlite database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# Engine with connect_args for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Ensure database directory and tables exist."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        Base.metadata.create_all(bind=engine)
