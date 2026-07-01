from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base
import enum


class SenderType(str, enum.Enum):
    CUSTOMER = "customer"
    BOT = "bot"
    ADMIN = "admin"


class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    country = Column(String(100), nullable=True)
    language = Column(String(10), default="en")
    first_contact = Column(DateTime(timezone=True), server_default=func.now())
    last_contact = Column(DateTime(timezone=True), onupdate=func.now())
    total_messages = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    
    messages = relationship("Message", back_populates="customer", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String(255), nullable=True)
    sender = Column(Enum(SenderType), nullable=False)
    message_text = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_read = Column(Boolean, default=False)
    reply_to = Column(Integer, ForeignKey("messages.id"), nullable=True)
    
    customer = relationship("Customer", back_populates="messages")
    replies = relationship("Message", remote_side=[id], backref="parent")


class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(String(500), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
