from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.config import settings
from app.constants import BRAND_NAME, BRAND_EMOJI, BRAND_TAGLINE
from app.services.message_service import MessageService
from app.services.analytics_service import AnalyticsService
from app.database.db import get_db
from app.utils.logger import logger

router = Router()
# ... rest of the code ...
