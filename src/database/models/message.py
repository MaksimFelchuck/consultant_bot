from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from .base import Base

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    role = Column(String)  # 'user' или 'assistant'
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    session_id = Column(String)
    user = relationship('User', back_populates='messages', lazy='joined') 