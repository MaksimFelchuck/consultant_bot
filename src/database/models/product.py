from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
import datetime
from .base import Base


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), index=True)
    description = Column(Text)
    price = Column(Integer, index=True)
    image_url = Column(String)
    specs = Column(JSON)  # Характеристики устройства (как JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    category_rel = relationship('Category', back_populates='products')

Index('ix_product_name', Product.name)
Index('ix_product_price', Product.price)
Index('ix_product_category_id', Product.category_id)
