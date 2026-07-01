import sys
from loguru import logger
from app.config import settings
import logging


def setup_logger():
    """Setup logger configuration for Annopow Bot."""
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # Add file handler
    logger.add(
        "logs/annopow_bot.log",
        rotation="500 MB",
        retention="10 days",
        level=settings.LOG_LEVEL
    )
    
    # Add error file handler
    logger.add(
        "logs/annopow_errors.log",
        rotation="100 MB",
        retention="30 days",
        level="ERROR"
    )
    
    # Set aiogram logging
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    
    logger.info(f"Logger initialized for {settings.BOT_NAME}")
    return logger
