from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from app.config import settings
from app.constants import BRAND_NAME, BRAND_EMOJI, WELCOME_MESSAGE, HELP_MESSAGE
from app.services.message_service import MessageService
from app.services.analytics_service import AnalyticsService
from app.database.db import get_db
from app.utils.logger import logger
import asyncio

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    user_id = message.from_user.id
    is_admin = user_id in settings.ADMIN_IDS
    
    db = next(get_db())
    service = MessageService(db)
    customer = service.get_or_create_customer(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language=message.from_user.language_code
    )
    
    if is_admin:
        stats = AnalyticsService(db).get_dashboard_stats()
        mode = service.get_current_mode()
        
        text = f"""
👋 *Welcome to {BRAND_NAME} Admin Panel!*

📊 *Dashboard Overview*
• Total Customers: {stats['total_customers']}
• Messages Today: {stats['messages_today']}
• Active Mode: {mode.upper()}

🔧 *Quick Commands:*
/auto - Enable auto mode
/manual - Enable manual mode
/stats - View statistics
/broadcast - Send broadcast
/customers - View customers

*{BRAND_EMOJI} {BRAND_NAME}*
"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Dashboard", callback_data="admin_dashboard")],
            [InlineKeyboardButton(text="👥 Customers", callback_data="admin_customers")],
            [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="📢 Telegram Ads", callback_data="admin_telegram_ads")]
        ])
        await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📦 Products", callback_data="products"),
             InlineKeyboardButton(text="📦 Orders", callback_data="orders")],
            [InlineKeyboardButton(text="📢 Telegram Ads Help", callback_data="telegram_ads_help"),
             InlineKeyboardButton(text="❓ FAQ", callback_data="faq")],
            [InlineKeyboardButton(text="📞 Contact", callback_data="contact")]
        ])
        await message.answer(WELCOME_MESSAGE, parse_mode="Markdown", reply_markup=keyboard)
    
    service.save_message(
        customer_id=customer.id,
        message_id=str(message.message_id),
        sender="customer",
        message_text=message.text or f"Started {BRAND_NAME} conversation"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    user_id = message.from_user.id
    is_admin = user_id in settings.ADMIN_IDS
    
    if is_admin:
        text = f"""
📚 *{BRAND_NAME} Admin Help*

🤖 /auto - Enable auto mode
👤 /manual - Enable manual mode
📊 /stats - View statistics
📢 /broadcast - Send broadcast
👥 /customers - View customers

*{BRAND_EMOJI} {BRAND_NAME}*
"""
    else:
        text = HELP_MESSAGE
    
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("auto"))
async def cmd_auto(message: Message):
    """Enable auto mode."""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Access denied.")
        return
    
    db = next(get_db())
    service = MessageService(db)
    service.set_mode("auto")
    
    await message.answer(
        f"🤖 *Auto Mode Enabled*\n\n"
        f"{BRAND_NAME} Bot will now reply automatically.\n"
        f"{BRAND_EMOJI} *{BRAND_NAME}*",
        parse_mode="Markdown"
    )


@router.message(Command("manual"))
async def cmd_manual(message: Message):
    """Enable manual mode."""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Access denied.")
        return
    
    db = next(get_db())
    service = MessageService(db)
    service.set_mode("manual")
    
    await message.answer(
        f"👤 *Manual Mode Enabled*\n\n"
        f"Messages will be forwarded to admins.\n"
        f"{BRAND_EMOJI} *{BRAND_NAME}*",
        parse_mode="Markdown"
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """View statistics."""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Access denied.")
        return
    
    db = next(get_db())
    service = AnalyticsService(db)
    stats = service.get_dashboard_stats()
    
    text = f"""
📊 *{BRAND_NAME} Statistics*

👥 Customers: {stats['total_customers']}
🆕 New Today: {stats['new_customers_today']}
📱 Active Now: {stats['active_customers']}

💬 Total Messages: {stats['total_messages']}
📩 Today: {stats['messages_today']}
⏱️ Avg Response: {stats['avg_response_time']}s

🤖 Mode: {stats['current_mode'].upper()}
🧠 AI: {stats['ai_enabled']}

{BRAND_EMOJI} *{BRAND_NAME}*
"""
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    """Send broadcast to all customers."""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Access denied.")
        return
    
    text = message.text.replace("/broadcast", "").strip()
    
    if not text:
        await message.answer(
            f"📢 *{BRAND_NAME} Broadcast*\n\n"
            f"Usage: `/broadcast Your message here`\n"
            f"Example: `/broadcast New products available! {BRAND_EMOJI}`",
            parse_mode="Markdown"
        )
        return
    
    db = next(get_db())
    service = MessageService(db)
    customers = service.get_all_customers()
    
    success = 0
    failed = 0
    
    for customer in customers:
        try:
            await message.bot.send_message(
                chat_id=customer.telegram_id,
                text=f"📢 *{BRAND_NAME} Announcement*\n\n{text}\n\n{BRAND_EMOJI} *{BRAND_NAME}*",
                parse_mode="Markdown"
            )
            success += 1
            await asyncio.sleep(0.1)
        except Exception as e:
            failed += 1
            logger.error(f"Broadcast failed to {customer.telegram_id}: {e}")
    
    await message.answer(
        f"📢 *Broadcast Complete*\n\n"
        f"✅ Sent: {success}\n"
        f"❌ Failed: {failed}\n"
        f"📊 Total: {len(customers)}\n\n"
        f"{BRAND_EMOJI} *{BRAND_NAME}*",
        parse_mode="Markdown"
    )


@router.message(Command("customers"))
async def cmd_customers(message: Message):
    """View customers list."""
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Access denied.")
        return
    
    db = next(get_db())
    service = MessageService(db)
    customers = service.get_all_customers()
    
    if not customers:
        await message.answer("No customers yet.")
        return
    
    text = f"👥 *{BRAND_NAME} Customers* ({len(customers)})\n\n"
    for i, customer in enumerate(customers[:20], 1):
        text += f"{i}. {customer.first_name or 'Unknown'} (@{customer.username or 'N/A'})\n"
        text += f"   ID: `{customer.telegram_id}` | Messages: {customer.total_messages}\n"
    
    if len(customers) > 20:
        text += f"\n... and {len(customers) - 20} more customers."
    
    await message.answer(text, parse_mode="Markdown")
