from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
import datetime
from .base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    email = Column(String)
    phone = Column(String)
    extra_data = Column(JSON)
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
