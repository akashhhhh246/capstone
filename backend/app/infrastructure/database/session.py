from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from app.infrastructure.configuration.config import settings
from app.domain.entities.models import Base
import os
import logging

logger = logging.getLogger("provenance_defense_db")

# Build engine
# If SQLite, use connect_args for multithreading and timeout
connect_args = {"check_same_thread": False, "timeout": 15} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

# Enterprise SQLite Pragma Configuration for High Concurrency (WAL Mode)
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA busy_timeout=15000")
            cursor.close()
        except Exception as e:
            logger.warning(f"Failed to set SQLite enterprise pragmas: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency for API endpoints to retrieve a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
