from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.orm import relationship
import datetime
from .base import Base

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    products = relationship('Product', back_populates='category_rel')

Index('ix_category_name', Category.name) 