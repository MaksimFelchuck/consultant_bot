import random

from sqlalchemy import func
from sqlalchemy.orm import Session

from .models import Category, Message, Product, User


# Получить случайные товары по всем категориям (top_n на категорию)
def get_random_products_by_category(session: Session, top_n: int = 10):
    result = {}
    categories = session.query(Category).all()
    for category in categories:
        # Берём больше товаров, чтобы выбрать уникальные по фото
        products = (
            session.query(Product)
            .filter(Product.category_id == category.id)
            .order_by(func.random())
            .limit(top_n * 3)
            .all()
        )
        unique = {}
        for p in products:
            if p.image_url not in unique and len(unique) < top_n:
                unique[p.image_url] = p
        result[category.name] = list(unique.values())
    return result


# Получить случайные товары по одной категории
def get_random_products_for_category(
    session: Session, category_id: int, top_n: int = 10
):
    return (
        session.query(Product)
        .filter(Product.category_id == category_id)
        .order_by(func.random())
        .limit(top_n)
        .all()
    )


# Сохранить сообщение
def save_message(
    session: Session, user_id: int, role: str, message: str, session_id: str = ""
):
    msg = Message(user_id=user_id, role=role, message=message, session_id=session_id)
    session.add(msg)
    session.commit()
    return msg


# Получить историю сообщений пользователя (по user_id, limit последних N)
def get_user_history(session: Session, user_id: int, limit: int = 10):
    return (
        session.query(Message)
        .filter(Message.user_id == user_id)
        .order_by(Message.timestamp.desc())
        .limit(limit)
        .all()
    )[
        ::-1
    ]  # вернуть в хронологическом порядке
