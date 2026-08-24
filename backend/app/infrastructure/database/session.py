from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.infrastructure.configuration.config import settings
from app.domain.entities.models import Base
import os

# Build engine
# If SQLite, use connect_args for multithreading
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

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
