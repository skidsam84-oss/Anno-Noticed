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

# Log database connection info (without password)
if database_url:
    try:
        # Extract host from URL for logging
        if "@" in database_url:
            host_part = database_url.split("@")[1].split("/")[0]
            logger.info(f"Connecting to database at: {host_part}")
        else:
            logger.info("Using default database connection")
    except Exception as e:
        logger.warning(f"Could not parse database URL: {e}")

# Create engine with Railway-specific settings
try:
    engine = create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        echo=settings.DEBUG,
        connect_args={
            "connect_timeout": 10,
        }
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    # Create engine with minimal settings as fallback
    engine = create_engine(
        database_url,
        pool_size=5,
        max_overflow=10,
        echo=settings.DEBUG,
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
