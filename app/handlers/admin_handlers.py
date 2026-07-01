from aiogram import Router, types, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.config import settings
from app.constants import BRAND_NAME, BRAND_EMOJI, BRAND_TAGLINE
from app.services.message_service import MessageService
from app.services.analytics_service import AnalyticsService
from app.database.db import get_db
from app.utils.logger import logger

router = Router()


@router.callback_query(F.data == "admin_dashboard")
async def admin_dashboard(callback: CallbackQuery):
    """Show admin dashboard."""
    await callback.answer("Loading dashboard...")
    
    db = next(get_db())
    analytics = AnalyticsService(db)
    stats = analytics.get_dashboard_stats()
    message_service = MessageService(db)
    mode = message_service.get_current_mode()
    
    text = f"""
📊 *{BRAND_NAME} Admin Dashboard*

📈 *Overview*
👥 Customers: {stats['total_customers']}
🆕 New Today: {stats['new_customers_today']}
📱 Active Now: {stats['active_customers']}

💬 *Messages*
📩 Total: {stats['total_messages']}
📨 Today: {stats['messages_today']}
⏱️ Avg Response: {stats['avg_response_time']}s

⚙️ *Settings*
🤖 Mode: {mode.upper()}
🧠 AI: {stats['ai_enabled']}

📅 Updated: {stats['last_updated']}

{BRAND_EMOJI} *{BRAND_TAGLINE}*
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👥 Customers", callback_data="admin_customers"),
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="🤖 Auto Mode", callback_data="admin_auto"),
            InlineKeyboardButton(text="👤 Manual Mode", callback_data="admin_manual")
        ],
        [
            InlineKeyboardButton(text="📢 Telegram Ads", callback_data="admin_telegram_ads"),
            InlineKeyboardButton(text="📊 Full Stats", callback_data="admin_stats")
        ]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data == "admin_customers")
async def admin_customers(callback: CallbackQuery):
    """Show customers list."""
    await callback.answer("Loading customers...")
    
    db = next(get_db())
    service = MessageService(db)
    customers = service.get_all_customers()
    
    if not customers:
        await callback.message.answer("No customers yet.")
        return
    
    text = f"👥 *{BRAND_NAME} Customers* ({len(customers)})\n\n"
    for i, customer in enumerate(customers[:10], 1):
        text += f"{i}. {customer.first_name or 'Unknown'} (@{customer.username or 'N/A'})\n"
        text += f"   ID: `{customer.telegram_id}` | Messages: {customer.total_messages}\n"
    
    if len(customers) > 10:
        text += f"\n... and {len(customers) - 10} more customers."
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Dashboard", callback_data="admin_dashboard")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery):
    """Show broadcast instructions."""
    await callback.answer()
    
    text = f"""
📢 *{BRAND_NAME} Broadcast*

Send a message to all your customers.

*Usage:*
`/broadcast Your message here`

*Example:*
`/broadcast New products just launched! {BRAND_EMOJI}`

💡 *Tips:*
• Keep messages short and clear
• Include {BRAND_EMOJI} for branding
• Use Markdown formatting if needed

*Your message will be sent to all {len(settings.ADMIN_IDS)} admins.*
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Dashboard", callback_data="admin_dashboard")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data == "admin_auto")
async def admin_auto(callback: CallbackQuery):
    """Enable auto mode from callback."""
    await callback.answer("Auto mode enabled!")
    
    db = next(get_db())
    service = MessageService(db)
    service.set_mode("auto")
    
    await callback.message.answer(
        f"🤖 *Auto Mode Enabled*\n\n"
        f"{BRAND_NAME} Bot will now reply automatically.\n"
        f"{BRAND_EMOJI} *{BRAND_NAME}*",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "admin_manual")
async def admin_manual(callback: CallbackQuery):
    """Enable manual mode from callback."""
    await callback.answer("Manual mode enabled!")
    
    db = next(get_db())
    service = MessageService(db)
    service.set_mode("manual")
    
    await callback.message.answer(
        f"👤 *Manual Mode Enabled*\n\n"
        f"Messages will be forwarded to admins.\n"
        f"{BRAND_EMOJI} *{BRAND_NAME}*",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Show statistics."""
    await callback.answer("Loading stats...")
    
    db = next(get_db())
    service = AnalyticsService(db)
    stats = service.get_dashboard_stats()
    
    text = f"""
📊 *{BRAND_NAME} Full Statistics*

👥 *Customers*
• Total: {stats['total_customers']}
• New Today: {stats['new_customers_today']}
• Active Now: {stats['active_customers']}

💬 *Messages*
• Total: {stats['total_messages']}
• Today: {stats['messages_today']}
• Avg Response: {stats['avg_response_time']}s

⚙️ *System*
• Mode: {stats['current_mode'].upper()}
• AI: {stats['ai_enabled']}
• Updated: {stats['last_updated']}

{BRAND_EMOJI} *{BRAND_TAGLINE}*
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Dashboard", callback_data="admin_dashboard")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data == "admin_telegram_ads")
async def admin_telegram_ads(callback: CallbackQuery):
    """Show Telegram Ads management."""
    await callback.answer("Loading Ads management...")
    
    text = f"""
📢 *{BRAND_NAME} Telegram Ads Management*

🎯 *Help customers with:*
• Ad optimization
• Targeting strategies
• Budget management
• Performance tracking
• Ad creative tips

📊 *Quick Tips to Share:*
1. Test different ad creatives
2. Use precise targeting
3. Monitor CTR and conversion rates
4. Optimize budget allocation
5. Retarget engaged users

💡 *Pro Tip:* Always A/B test your ads!

{BRAND_EMOJI} *{BRAND_TAGLINE}*
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Ads Statistics", callback_data="ads_stats")],
        [InlineKeyboardButton(text="🔙 Back to Dashboard", callback_data="admin_dashboard")]
    ])
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
