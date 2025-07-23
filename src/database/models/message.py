import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)  # 'user' или 'assistant'
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    session_id = Column(String)  # Для группировки по сессиям, если нужно
    user = relationship("User", back_populates="messages", lazy="joined")
