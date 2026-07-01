from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from app.config import settings
from app.constants import BRAND_NAME, BRAND_EMOJI, WELCOME_MESSAGE, HELP_MESSAGE
from app.services.message_service import MessageService
from app.services.analytics_service import AnalyticsService
from app.database.db import get_db
from app.utils.logger import logger
import asyncio

router = Router()
# ... rest of the code ...
