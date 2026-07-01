from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime
from app.database.models import Customer
import logging

logger = logging.getLogger(__name__)


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create(self, telegram_id: int, **kwargs) -> Customer:
        """Get or create a customer."""
        customer = self.db.query(Customer).filter(
            Customer.telegram_id == telegram_id
        ).first()
        
        if not customer:
            customer = Customer(telegram_id=telegram_id, **kwargs)
            self.db.add(customer)
            self.db.commit()
            self.db.refresh(customer)
            logger.info(f"Created new customer: {telegram_id}")
        else:
            update_data = {
                'first_name': kwargs.get('first_name', customer.first_name),
                'last_name': kwargs.get('last_name', customer.last_name),
                'username': kwargs.get('username', customer.username),
                'last_contact': datetime.utcnow()
            }
            for key, value in update_data.items():
                if value:
                    setattr(customer, key, value)
            self.db.commit()
            self.db.refresh(customer)
        
        return customer
    
    def get_by_telegram_id(self, telegram_id: int) -> Optional[Customer]:
        return self.db.query(Customer).filter(
            Customer.telegram_id == telegram_id
        ).first()
    
    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        return self.db.query(Customer).filter(
            Customer.id == customer_id
        ).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        return self.db.query(Customer).offset(skip).limit(limit).all()
    
    def get_active_customers(self) -> List[Customer]:
        return self.db.query(Customer).filter(
            Customer.is_active == True,
            Customer.is_blocked == False
        ).all()
    
    def get_new_customers_today(self) -> int:
        today = datetime.utcnow().date()
        return self.db.query(Customer).filter(
            func.date(Customer.first_contact) == today
        ).count()
    
    def get_total_customers(self) -> int:
        return self.db.query(Customer).count()
    
    def increment_messages(self, customer_id: int):
        customer = self.get_by_id(customer_id)
        if customer:
            customer.total_messages += 1
            self.db.commit()
    
    def update_last_contact(self, customer_id: int):
        customer = self.get_by_id(customer_id)
        if customer:
            customer.last_contact = datetime.utcnow()
            self.db.commit()
