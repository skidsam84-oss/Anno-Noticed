from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from app.config import settings
from app.utils.logger import logger


class AuthMiddleware(BaseMiddleware):
    """Authentication middleware for admin commands."""
    
    ADMIN_COMMANDS = ['/dashboard', '/stats', '/broadcast', '/customers', '/auto', '/manual']
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """Check if user is authorized."""
        user_id = event.from_user.id
        
        # Get admin IDs as list
        admin_ids = settings.ADMIN_IDS if isinstance(settings.ADMIN_IDS, list) else []
        
        # Check if this is an admin-only command
        if hasattr(event, 'text') and event.text:
            if any(event.text.startswith(cmd) for cmd in self.ADMIN_COMMANDS):
                if user_id not in admin_ids:
                    await event.answer("⛔ Access denied. You are not an admin.")
                    return
        
        return await handler(event, data)
