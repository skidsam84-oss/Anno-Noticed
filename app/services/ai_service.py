import openai
from typing import Optional
from app.config import settings
from app.constants import BRAND_NAME, BRAND_EMOJI
from app.utils.logger import logger
from app.database.db import get_db
from app.database.repositories.customer_repository import CustomerRepository


class AIService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.enabled = True
        else:
            self.enabled = False
            logger.warning("OpenAI API key not configured.")
    
    async def get_response(self, user_message: str, customer_id: Optional[int] = None) -> Optional[str]:
        if not self.enabled:
            return None
        
        try:
            system_prompt = f"""You are {BRAND_NAME} Support Assistant.
            
Company: {BRAND_NAME}
Emoji: {BRAND_EMOJI}

Be friendly, professional, and concise. Help with products, orders, and Telegram Ads.
Include {BRAND_EMOJI} in responses."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI service error: {e}")
            return None
    
    async def get_suggested_reply(self, user_message: str, context: str = "") -> Optional[str]:
        if not self.enabled:
            return None
        
        try:
            messages = [
                {"role": "system", "content": f"You are a {BRAND_NAME} support assistant. Provide a professional reply."},
                {"role": "user", "content": f"Customer: {user_message}\nContext: {context}\n\nSuggested reply:"}
            ]
            
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI suggestion error: {e}")
            return None
