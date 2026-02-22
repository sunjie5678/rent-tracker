"""Database session management for Flask application."""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import Config

# Create engine with connection pooling
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Scoped session for thread safety
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def init_db():
    """Initialize database - create all tables."""
    from app.models.base import Base

    Base.metadata.create_all(bind=engine)


def shutdown_session(exception=None):
    """Remove database session at end of request."""
    db_session.remove()
