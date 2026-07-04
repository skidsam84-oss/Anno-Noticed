import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from app.config import settings
from app.constants import BRAND_NAME, BRAND_EMOJI
from app.database.db import init_db
from app.handlers import commands, admin_handlers, buyer_handlers
from app.middlewares.auth import AuthMiddleware
from app.utils.logger import setup_logger
import redis.asyncio as redis

logger = setup_logger()


async def set_commands(bot: Bot):
    """Set bot commands."""
    commands_list = [
        BotCommand(command="start", description=f"🚀 Start {BRAND_NAME} Bot"),
        BotCommand(command="help", description="❓ Get help"),
        BotCommand(command="auto", description="🤖 Enable auto mode"),
        BotCommand(command="manual", description="👤 Enable manual mode"),
        BotCommand(command="stats", description="📊 View statistics"),
        BotCommand(command="broadcast", description="📢 Send broadcast"),
        BotCommand(command="customers", description="👥 View customers"),
    ]
    await bot.set_my_commands(commands_list, scope=BotCommandScopeDefault())


async def on_startup(bot: Bot):
    """Actions on bot startup."""
    logger.info(f"Starting {BRAND_NAME} Bot...")
    
    # Log admin IDs for debugging
    logger.info(f"Admin IDs loaded: {settings.ADMIN_IDS}")
    
    # Print database URL for debugging (hidden password)
    if settings.DATABASE_URL:
        db_info = settings.DATABASE_URL.split("@")
        if len(db_info) > 1:
            logger.info(f"Database: Connected to {db_info[1].split('/')[0]}")
        else:
            logger.info("Database: Using default")
    
    # Initialize database (with error handling)
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        logger.warning("Bot will continue without database...")
    
    # Set commands
    await set_commands(bot)
    logger.info("Commands set")
    
    # Notify admins
    admin_ids = settings.ADMIN_IDS if isinstance(settings.ADMIN_IDS, list) else []
    for admin_id in admin_ids:
        try:
            await bot.send_message(
                admin_id,
                f"{BRAND_EMOJI} *{BRAND_NAME} Bot Started Successfully!*\n\n"
                f"Mode: {settings.DEFAULT_MODE.upper()}\n"
                f"AI: {'Enabled' if settings.ENABLE_AI else 'Disabled'}\n"
                f"Database: {'Connected' if settings.DATABASE_URL else 'Not configured'}",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    logger.info(f"{BRAND_NAME} Bot startup complete!")


async def on_shutdown(bot: Bot):
    """Actions on bot shutdown."""
    logger.info(f"Shutting down {BRAND_NAME} Bot...")
    
    # Notify admins
    admin_ids = settings.ADMIN_IDS if isinstance(settings.ADMIN_IDS, list) else []
    for admin_id in admin_ids:
        try:
            await bot.send_message(
                admin_id,
                f"🛑 *{BRAND_NAME} Bot is shutting down...*",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")
    
    # Close database connections
    try:
        from app.database.db import engine
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
    
    logger.info(f"{BRAND_NAME} Bot shutdown complete!")


async def main():
    """Main function."""
    # Initialize bot with default settings
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    
    # Setup storage
    if settings.REDIS_URL:
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            storage = RedisStorage(redis=redis_client)
            logger.info("Using Redis storage")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using Memory storage.")
            storage = MemoryStorage()
    else:
        storage = MemoryStorage()
        logger.info("Using Memory storage")
    
    # Initialize dispatcher
    dp = Dispatcher(storage=storage)
    
    # Register middlewares
    dp.message.middleware(AuthMiddleware())
    logger.info("Middlewares registered")
    
    # Register routers
    dp.include_router(commands.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(buyer_handlers.router)
    logger.info("Handlers registered")
    
    # Setup startup/shutdown
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Start polling
    logger.info("Starting polling...")
    
    try:
        await dp.start_polling(
            bot,
            allowed_updates=["message", "callback_query"],
            skip_updates=True
        )
    except Exception as e:
        logger.error(f"Polling error: {e}")
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
