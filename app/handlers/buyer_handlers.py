from aiogram import Router, types, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.config import settings
from app.constants import (
    BRAND_NAME, BRAND_EMOJI, BRAND_TAGLINE,
    AUTO_REPLY_MESSAGE, MANUAL_REPLY_MESSAGE,
    TELEGRAM_ADS_KEYWORDS
)
from app.services.message_service import MessageService
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService
from app.database.db import get_db
from app.utils.logger import logger
import asyncio

router = Router()
# ... rest of the code ...
