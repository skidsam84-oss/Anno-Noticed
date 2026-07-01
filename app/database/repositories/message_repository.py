from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime
from app.database.models import Message


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, customer_id: int, sender: str, message_text: str, 
               message_id: Optional[str] = None) -> Message:
        message = Message(
            customer_id=customer_id,
            message_id=message_id,
            sender=sender,
            message_text=message_text,
            timestamp=datetime.utcnow()
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_customer_messages(self, customer_id: int, limit: int = 50) -> List[Message]:
        return self.db.query(Message).filter(
            Message.customer_id == customer_id
        ).order_by(desc(Message.timestamp)).limit(limit).all()
    
    def get_messages_today(self) -> int:
        today = datetime.utcnow().date()
        return self.db.query(Message).filter(
            Message.timestamp >= today
        ).count()
    
    def get_total_messages(self) -> int:
        return self.db.query(Message).count()
