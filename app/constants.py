"""Annopow Brand Constants"""

# Brand Information
BRAND_NAME = "Annopow"
BRAND_TAGLINE = "Powering Your Success"
BRAND_EMOJI = "⚡"
BRAND_COLOR = "#FF6B00"  # Energetic Orange
BRAND_WEBSITE = "https://annopow.com"
BRAND_EMAIL = "support@annopow.com"

# Bot Messages
WELCOME_MESSAGE = f"""
{BRAND_EMOJI} *Welcome to {BRAND_NAME} Support!*

I'm your AI-powered assistant here to help you with:
• Product information
• Order support
• Technical assistance
• Telegram Ads optimization

*How can I help you today?*
"""

HELP_MESSAGE = f"""
❓ *{BRAND_NAME} Support Help*

🤖 *How to use this bot:*
Simply send me a message and I'll help you!

📝 *Common topics:*
• Product information
• Pricing and availability
• Order tracking
• Returns and refunds
• Telegram Ads help

⏰ *Response Time:*
We aim to respond within 24 hours

📞 *Need immediate help?*
Contact our support team at {BRAND_EMAIL}
"""

AUTO_REPLY_MESSAGE = f"""
{BRAND_EMOJI} *Thank you for your message!*

Our AI assistant is processing your request and will respond shortly.

*Best regards,*
*{BRAND_NAME} Support Team*
"""

MANUAL_REPLY_MESSAGE = f"""
✅ *Your message has been received!*

Our {BRAND_NAME} support team will review and respond to you shortly.

*Average response time: < 24 hours*

Thank you for choosing {BRAND_NAME}! {BRAND_EMOJI}
"""

ADMIN_WELCOME = f"""
👋 *Welcome to {BRAND_NAME} Admin Panel!*

📊 *Dashboard Overview*
• Total Customers: {{total_customers}}
• Messages Today: {{messages_today}}
• Active Mode: {{mode}}

🔧 *Quick Commands:*
/auto - Enable auto mode
/manual - Enable manual mode
/stats - View statistics
/broadcast - Send broadcast
/customers - View customers

*{BRAND_TAGLINE}* {BRAND_EMOJI}
"""

# FAQ Categories
FAQ_CATEGORIES = {
    "products": "Product Information",
    "orders": "Order & Shipping",
    "returns": "Returns & Refunds",
    "technical": "Technical Support",
    "telegram_ads": "Telegram Ads Help",
    "general": "General Questions"
}

# Telegram Ads Keywords for detection
TELEGRAM_ADS_KEYWORDS = [
    "telegram ads", "fix ads", "ad problem", "ads not working",
    "telegram ad", "ad issue", "ad fix", "telegram advertising",
    "telegram promotion", "telegram marketing", "telegram campaign"
]

# Auto-reply responses
DEFAULT_RESPONSES = {
    "greeting": [
        f"Hello! Welcome to {BRAND_NAME}! How can I assist you today? {BRAND_EMOJI}",
        f"Hi there! Thanks for reaching out to {BRAND_NAME}. What can I help you with?",
        f"Greetings! This is {BRAND_NAME} Support. How may I help you?"
    ],
    "telegram_ads": [
        f"📢 *Telegram Ads Help*\n\nI can help you with:\n• Ad optimization\n• Targeting strategies\n• Budget management\n• Performance tracking\n\nWhat specific aspect of Telegram Ads do you need help with? {BRAND_EMOJI}",
        f"🎯 *Telegram Ads Support*\n\nOur specialists can help you:\n1. Create effective ads\n2. Target the right audience\n3. Optimize your budget\n4. Improve conversion rates\n\nTell me more about your ad goals! {BRAND_EMOJI}"
    ],
    "thanks": [
        f"You're welcome! Is there anything else I can help you with? {BRAND_EMOJI}",
        f"My pleasure! Don't hesitate to ask if you need anything else."
    ],
    "fallback": [
        f"I understand you're asking about {BRAND_NAME}. Let me get you the right information.",
        f"Thank you for your question about {BRAND_NAME}. I'll help you with that."
    ]
}

# Support Hours
SUPPORT_HOURS = {
    "weekday": "9:00 AM - 6:00 PM",
    "weekend": "10:00 AM - 4:00 PM",
    "timezone": "UTC"
}
