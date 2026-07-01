# ⚡ Annopow Support Bot

AI-powered Telegram customer support bot for Annopow brand.

## Features

- 🤖 **Auto Mode**: AI-powered automatic replies
- 👤 **Manual Mode**: Forward messages to admins
- 🧠 **AI Integration**: OpenAI GPT support
- 📊 **Analytics**: Customer and message statistics
- 👥 **Customer Management**: Full database
- 📢 **Broadcast**: Send messages to all customers
- 🔒 **Secure**: Admin-only commands

## Deploy on Railway

1. Fork this repository on GitHub
2. Create a new project on Railway
3. Connect your GitHub repository
4. Add environment variables:
   - `BOT_TOKEN`: Your bot token
   - `ADMIN_IDS`: Your Telegram ID
   - `ENABLE_AI`: true/false
   - `OPENAI_API_KEY`: Your API key (optional)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy .env file
cp .env.example .env

# Run the bot
python -m app.main
