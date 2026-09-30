"""Database connection setup and session management.

Configures SQLAlchemy engine, session maker, and provides a database
session generator for FastAPI dependency injection.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# Create the database engine with connection ping enabled
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

# Database session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy database models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """Provide a transactional database session for each request.

    Closes the session automatically when the request finishes.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
