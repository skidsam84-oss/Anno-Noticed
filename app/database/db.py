from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Get database URL from settings
database_url = settings.DATABASE_URL

# For Railway, we need to ensure the URL uses the correct format
if database_url and "postgres" in database_url:
    # Railway provides DATABASE_URL with correct credentials
    logger.info(f"Using database: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'configured'}")
else:
    logger.warning("No DATABASE_URL found, using default")

# Create engine with Railway-specific settings
engine = create_engine(
    database_url,
    pool_size=20,
    max_overflow=40,
    pool_timeout=60,
    pool_recycle=3600,
    echo=settings.DEBUG,
    # For Railway's PostgreSQL
    connect_args={
        "connect_timeout": 10,
    } if "postgres" in database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        # Don't raise - let the bot continue without database if needed
        # This allows the bot to run even if DB connection fails
        logger.warning("Continuing without database connection...")
