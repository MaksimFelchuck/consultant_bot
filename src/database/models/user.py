import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String, BigInteger
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    email = Column(String)
    phone = Column(String)
    extra_data = Column(JSON)
    messages = relationship("Message", back_populates="user", lazy="dynamic")
