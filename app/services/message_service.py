from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.models import Customer, Message, SystemSetting
from app.database.repositories.customer_repository import CustomerRepository
from app.database.repositories.message_repository import MessageRepository
from app.utils.logger import logger


class MessageService:
    def __init__(self, db: Session):
        self.db = db
        self.customer_repo = CustomerRepository(db)
        self.message_repo = MessageRepository(db)
    
    def get_or_create_customer(self, telegram_id: int, **kwargs) -> Customer:
        return self.customer_repo.get_or_create(telegram_id, **kwargs)
    
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        return self.customer_repo.get_by_id(customer_id)
    
    def get_customer_by_telegram_id(self, telegram_id: int) -> Optional[Customer]:
        return self.customer_repo.get_by_telegram_id(telegram_id)
    
    def save_message(self, customer_id: int, sender: str, message_text: str, 
                     message_id: Optional[str] = None) -> Message:
        message = self.message_repo.create(
            customer_id=customer_id,
            sender=sender,
            message_text=message_text,
            message_id=message_id
        )
        self.customer_repo.increment_messages(customer_id)
        self.customer_repo.update_last_contact(customer_id)
        logger.info(f"Message saved: {message.id} from {sender}")
        return message
    
    def get_customer_messages(self, customer_id: int, limit: int = 50):
        return self.message_repo.get_customer_messages(customer_id, limit)
    
    def get_current_mode(self) -> str:
        setting = self.db.query(SystemSetting).filter(
            SystemSetting.key == "current_mode"
        ).first()
        
        if not setting:
            setting = SystemSetting(
                key="current_mode",
                value="auto",
                description="Current operation mode: auto or manual"
            )
            self.db.add(setting)
            self.db.commit()
            self.db.refresh(setting)
        
        return setting.value
    
    def set_mode(self, mode: str):
        setting = self.db.query(SystemSetting).filter(
            SystemSetting.key == "current_mode"
        ).first()
        
        if not setting:
            setting = SystemSetting(
                key="current_mode",
                value=mode,
                description="Current operation mode"
            )
            self.db.add(setting)
        else:
            setting.value = mode
        
        self.db.commit()
        logger.info(f"Mode set to: {mode}")
    
    def get_customer_count(self) -> int:
        return self.customer_repo.get_total_customers()
    
    def get_messages_today(self) -> int:
        return self.message_repo.get_messages_today()
    
    def get_all_customers(self) -> List[Customer]:
        return self.customer_repo.get_all()
    
    def get_active_customers(self) -> List[Customer]:
        return self.customer_repo.get_active_customers()
