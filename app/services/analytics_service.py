from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database.models import Customer, Message
from app.utils.logger import logger
from typing import Dict, Any


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        today = datetime.utcnow().date()
        
        total_customers = self.db.query(Customer).count()
        new_customers_today = self.db.query(Customer).filter(
            func.date(Customer.first_contact) == today
        ).count()
        
        active_time = datetime.utcnow() - timedelta(minutes=30)
        active_customers = self.db.query(Customer).filter(
            Customer.last_contact >= active_time
        ).count()
        
        total_messages = self.db.query(Message).count()
        messages_today = self.db.query(Message).filter(
            func.date(Message.timestamp) == today
        ).count()
        
        avg_response_time = self.calculate_avg_response_time()
        
        from app.services.message_service import MessageService
        message_service = MessageService(self.db)
        current_mode = message_service.get_current_mode()
        
        from app.config import settings
        ai_enabled = settings.ENABLE_AI
        
        return {
            "total_customers": total_customers,
            "new_customers_today": new_customers_today,
            "active_customers": active_customers,
            "total_messages": total_messages,
            "messages_today": messages_today,
            "avg_response_time": avg_response_time,
            "current_mode": current_mode,
            "ai_enabled": "✅ Enabled" if ai_enabled else "❌ Disabled",
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    
    def calculate_avg_response_time(self) -> int:
        try:
            customer_messages = self.db.query(Message).filter(
                Message.sender == "customer"
            ).order_by(Message.timestamp).limit(100).all()
            
            if not customer_messages:
                return 0
            
            total_time = 0
            count = 0
            
            for msg in customer_messages:
                response = self.db.query(Message).filter(
                    Message.customer_id == msg.customer_id,
                    Message.timestamp > msg.timestamp,
                    Message.sender.in_(["bot", "admin"])
                ).order_by(Message.timestamp).first()
                
                if response:
                    time_diff = (response.timestamp - msg.timestamp).total_seconds()
                    if time_diff < 3600:
                        total_time += time_diff
                        count += 1
            
            return int(total_time / count) if count > 0 else 0
            
        except Exception as e:
            logger.error(f"Error calculating avg response time: {e}")
            return 0
    
    def track_message(self, customer_id: int):
        pass
