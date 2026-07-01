from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from app.config import settings
from app.constants import BRAND_NAME, BRAND_EMOJI, AUTO_REPLY_MESSAGE, MANUAL_REPLY_MESSAGE
from app.services.message_service import MessageService
from app.services.ai_service import AIService
from app.services.analytics_service import AnalyticsService
from app.database.db import get_db
from app.utils.logger import logger
import asyncio

router = Router()

# Keywords for different categories
KEYWORDS = {
    "telegram_ads": ["telegram ads", "fix ads", "ad problem", "ads not working", "telegram ad", "ad issue", "ad fix"],
    "pricing": ["price", "cost", "how much", "pricing", "fee", "charge"],
    "shipping": ["shipping", "delivery", "track", "where is my order", "shipping cost"],
    "support": ["help", "assist", "support", "agent", "human"],
    "product": ["product", "item", "what do you sell", "catalog"],
}

@router.message(F.text)
async def handle_buyer_message(message: Message):
    """Handle all buyer messages."""
    user_id = message.from_user.id
    
    # Skip if admin
    if user_id in settings.ADMIN_IDS:
        return
    
    db = next(get_db())
    message_service = MessageService(db)
    analytics_service = AnalyticsService(db)
    
    # Get or create customer
    customer = message_service.get_or_create_customer(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language=message.from_user.language_code
    )
    
    # Save message
    saved_message = message_service.save_message(
        customer_id=customer.id,
        message_id=str(message.message_id),
        sender="customer",
        message_text=message.text
    )
    
    # Update analytics
    analytics_service.track_message(customer.id)
    
    # Check current mode
    current_mode = message_service.get_current_mode()
    
    # Detect if it's about Telegram Ads
    is_telegram_ad_query = detect_telegram_ad_query(message.text)
    
    if current_mode == "auto":
        # Auto reply
        await handle_auto_reply(message, customer, message_service, is_telegram_ad_query)
    else:
        # Manual mode - forward to admins
        await handle_manual_mode(message, customer, message_service)


def detect_telegram_ad_query(text: str) -> bool:
    """Detect if the message is about Telegram Ads."""
    text_lower = text.lower()
    for keyword in KEYWORDS["telegram_ads"]:
        if keyword in text_lower:
            return True
    return False


async def handle_auto_reply(message: Message, customer, message_service, is_telegram_ad_query: bool = False):
    """Handle auto reply mode with Annopow branding."""
    try:
        # Send typing indicator
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        # Check if it's a Telegram Ads query
        if is_telegram_ad_query:
            response = f"""
{BRAND_EMOJI} *Thank you for reaching out to {BRAND_NAME}!*

I understand you need help with Telegram Ads. Here's what we can do:

📌 *Quick Solutions:*
1. Make sure your ad budget is sufficient
2. Check your targeting settings
3. Verify your ad creative meets Telegram guidelines
4. Ensure your bot is properly set up

🔧 *Need more help?*
Our support team can assist you with:
• Ad optimization
• Targeting strategies
• Budget recommendations
• Performance tracking

*To get personalized help:*
1. Tell me your ad budget
2. What's your target audience?
3. What's your goal? (leads, sales, awareness)

{BRAND_EMOJI} *{BRAND_NAME} Support Team*

_P.S. I'm forwarding this to our ad specialist for detailed assistance!_ ✨
"""
            await message.answer(response, parse_mode="Markdown")
            
            # Save bot message
            message_service.save_message(
                customer_id=customer.id,
                sender="bot",
                message_text="Sent Telegram Ads support response"
            )
            
            # Notify admins for follow-up
            await notify_admins(message, customer, "Telegram Ads inquiry - needs follow-up")
            return
        
        # Try AI response first
        ai_response = None
        if settings.ENABLE_AI and settings.OPENAI_API_KEY:
            ai_service = AIService()
            ai_response = await ai_service.get_response(
                message.text,
                customer_id=customer.id
            )
        
        if ai_response:
            # Send AI response with branding
            response_text = f"{ai_response}\n\n{BRAND_EMOJI} *{BRAND_NAME} Support*"
            await message.answer(response_text, parse_mode="Markdown")
            
            # Save bot message
            message_service.save_message(
                customer_id=customer.id,
                sender="bot",
                message_text=ai_response
            )
            
            logger.info(f"AI response sent to {customer.telegram_id}")
        else:
            # Fallback with Telegram Ads detection
            if is_telegram_ad_query:
                fallback = f"""
{BRAND_EMOJI} *Thank you for your message about Telegram Ads!*

Our team specializes in helping businesses like yours succeed with Telegram advertising.

📊 *We can help you:*
• Optimize ad performance
• Reduce cost per lead
• Improve targeting
• Track conversions

*To get started:*
1. Share your current ad metrics
2. Tell us your target audience
3. What's your daily budget?

*Our ad specialist will respond within 2 hours!* ⏰

{BRAND_EMOJI} *{BRAND_NAME} Ads Team*
"""
            else:
                fallback = f"""
{BRAND_EMOJI} *Thank you for your message!*

I'm here to help you with:
• Product information
• Order support
• Technical assistance
• Telegram Ads optimization

*How can I help you today?*

{BRAND_EMOJI} *{BRAND_NAME} Support*
"""
            await message.answer(fallback, parse_mode="Markdown")
            
            # Notify admins
            await notify_admins(message, customer, "Fallback response used")
    
    except Exception as e:
        logger.error(f"Auto reply error: {e}")
        await message.answer(
            f"I'm having trouble processing your request. "
            f"Our {BRAND_NAME} team has been notified.\n\n"
            f"{BRAND_EMOJI} *{BRAND_NAME} Support*",
            parse_mode="Markdown"
        )
        await notify_admins(message, customer, f"Error: {str(e)}")


async def handle_manual_mode(message: Message, customer, message_service):
    """Handle manual mode - forward to admins."""
    try:
        # Send typing indicator
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        # Check if it's a Telegram Ads query
        is_telegram_ad_query = detect_telegram_ad_query(message.text)
        
        # Forward message to all admins
        for admin_id in settings.ADMIN_IDS:
            try:
                # Forward the message
                forwarded = await message.bot.forward_message(
                    chat_id=admin_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
                
                # Add reply keyboard
                from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="💬 Reply",
                            callback_data=f"reply_{customer.id}_{message.message_id}"
                        ),
                        InlineKeyboardButton(
                            text="📋 Customer Info",
                            callback_data=f"info_{customer.id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="💡 AI Suggestion",
                            callback_data=f"suggest_{customer.id}_{message.message_id}"
                        ),
                        InlineKeyboardButton(
                            text="📢 Telegram Ads Expert",
                            callback_data=f"ads_expert_{customer.id}"
                        )
                    ]
                ])
                
                # Check if it's about Telegram Ads
                ad_tag = "🔴 *TELEGRAM ADS INQUIRY* 🔴\n\n" if is_telegram_ad_query else ""
                
                # Send customer info with Annopow branding
                info_text = f"""
{ad_tag}👤 *New Message from Customer*

🏷️ *Brand:* {BRAND_NAME}
🆔 ID: `{customer.telegram_id}`
👤 Name: {customer.first_name or 'N/A'} {customer.last_name or ''}
📝 Username: @{customer.username or 'N/A'}
🌍 Country: {customer.country or 'Unknown'}
🗣️ Language: {customer.language or 'Unknown'}
💬 Total Messages: {customer.total_messages}

📝 *Message:*
{message.text}

{BRAND_EMOJI} *{BRAND_NAME}*
"""
                
                await message.bot.send_message(
                    admin_id,
                    info_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
                
                logger.info(f"Message forwarded to admin {admin_id}")
                
            except Exception as e:
                logger.error(f"Failed to forward to admin {admin_id}: {e}")
        
        # Acknowledge to customer with branding
        if is_telegram_ad_query:
            await message.answer(f"""
✅ *Your message about Telegram Ads has been received!*

Our {BRAND_NAME} Ads specialist will review your query and respond shortly.

⏰ *Response time: < 2 hours*

*In the meantime, you can:*
1. Share your ad budget
2. Tell us your target audience
3. What's your conversion goal?

{BRAND_EMOJI} *{BRAND_NAME} Ads Team*
""", parse_mode="Markdown")
        else:
            await message.answer(MANUAL_REPLY_MESSAGE, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Manual mode error: {e}")
        await message.answer(
            f"⚠️ There was an error. Please try again later.\n\n"
            f"{BRAND_EMOJI} *{BRAND_NAME} Support*",
            parse_mode="Markdown"
        )


async def notify_admins(message: Message, customer, context: str = ""):
    """Notify admins about customer interaction with Annopow branding."""
    is_telegram_ad = detect_telegram_ad_query(message.text)
    
    for admin_id in settings.ADMIN_IDS:
        try:
            ad_tag = "🔴 *TELEGRAM ADS INQUIRY* 🔴\n" if is_telegram_ad else ""
            
            text = f"""
🔔 *{BRAND_NAME} Customer Interaction*

{ad_tag}👤 *Customer:* {customer.first_name or 'Unknown'}
🆔 *ID:* `{customer.telegram_id}`
💬 *Message:* {message.text[:100]}...
📌 *Context:* {context}

{BRAND_EMOJI} *{BRAND_TAGLINE}*
"""
            
            await message.bot.send_message(
                admin_id,
                text,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")


@router.callback_query(F.data.startswith("reply_"))
async def handle_reply_callback(callback: CallbackQuery):
    """Handle reply button callback."""
    await callback.answer(f"Use /reply to respond as {BRAND_NAME} Support")
    await callback.message.answer(
        f"To reply to this {BRAND_NAME} customer, use:\n"
        f"/reply {callback.data.split('_')[1]} [your message]\n\n"
        f"💡 Tip: Your message will be sent as {BRAND_NAME} Support"
    )


@router.callback_query(F.data.startswith("ads_expert_"))
async def handle_ads_expert_callback(callback: CallbackQuery):
    """Handle ads expert callback."""
    customer_id = int(callback.data.split('_')[2])
    
    await callback.answer("📢 Assigning to Ads Expert...")
    await callback.message.answer(
        f"✅ *Ads Expert Assigned!*\n\n"
        f"A {BRAND_NAME} Telegram Ads specialist will contact this customer.\n\n"
        f"📋 *Expert Checklist:*\n"
        f"1. Review ad budget\n"
        f"2. Check targeting settings\n"
        f"3. Analyze ad performance\n"
        f"4. Provide optimization recommendations\n\n"
        f"💡 *Pro Tip:* Ask the customer about their conversion goals!\n\n"
        f"{BRAND_EMOJI} *{BRAND_NAME} Ads Team*",
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("suggest_"))
async def handle_suggest_callback(callback: CallbackQuery):
    """Handle AI suggestion callback."""
    await callback.answer("Generating AI suggestion...")
    
    if settings.ENABLE_AI and settings.OPENAI_API_KEY:
        ai_service = AIService()
        suggestion = await ai_service.get_suggested_reply(
            "Customer message about Telegram Ads",
            f"Brand: {BRAND_NAME}\nCustomer asking about Telegram Ads support"
        )
        
        if suggestion:
            await callback.message.answer(
                f"💡 *AI Suggested Reply for {BRAND_NAME}*\n\n"
                f"{suggestion}\n\n"
                f"📌 *Tip:* Edit and send using /reply",
                parse_mode="Markdown"
            )
        else:
            await callback.message.answer(
                f"🤖 AI suggestion unavailable. Please craft your own reply.\n\n"
                f"{BRAND_EMOJI} *{BRAND_NAME}*",
                parse_mode="Markdown"
            )
    else:
        await callback.message.answer(
            f"🤖 AI is not enabled. Please enable OpenAI to use this feature.\n\n"
            f"{BRAND_EMOJI} *{BRAND_NAME}*",
            parse_mode="Markdown"
        )


@router.callback_query(F.data.startswith("info_"))
async def handle_info_callback(callback: CallbackQuery):
    """Handle customer info callback."""
    customer_id = int(callback.data.split('_')[1])
    
    db = next(get_db())
    service = MessageService(db)
    customer = service.get_customer(customer_id)
    
    if customer:
        text = f"""
📋 *{BRAND_NAME} Customer Information*

🆔 Telegram ID: `{customer.telegram_id}`
👤 Name: {customer.first_name or 'N/A'} {customer.last_name or ''}
📝 Username: @{customer.username or 'N/A'}
🌍 Country: {customer.country or 'Unknown'}
🗣️ Language: {customer.language or 'Unknown'}
📅 First Contact: {customer.first_contact}
🔄 Last Contact: {customer.last_contact}
💬 Total Messages: {customer.total_messages}
✅ Status: {'Active' if customer.is_active else 'Inactive'}

{BRAND_EMOJI} *{BRAND_TAGLINE}*
"""
        
        await callback.message.answer(text, parse_mode="Markdown")
    
    await callback.answer()
