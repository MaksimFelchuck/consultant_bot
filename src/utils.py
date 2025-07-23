"""
Утилитарные функции для бота ТехноМаркет.
"""

import hashlib
import json
import logging
import re
from pathlib import Path

from aiogram import Router
from aiogram.types import Message

from database import SessionLocal
from database.models import Product
from database.service import get_or_create_user


def get_category_by_keywords(user_message):
    """Определяет категорию товара по ключевым словам."""
    mapping = {
        "телефон": "Смартфоны",
        "смартфон": "Смартфоны",
        "мобильник": "Смартфоны",
        "айфон": "Смартфоны",
        "iphone": "Смартфоны",
        "планшет": "Планшеты",
        "ноутбук": "Ноутбуки",
        "макбук": "Ноутбуки",
        "телевизор": "Телевизоры",
        "наушники": "Наушники",
        "часы": "Смарт-часы",
        "apple watch": "Смарт-часы",
        "камера": "Фотоаппараты",
        "фотоаппарат": "Фотоаппараты",
        "приставка": "Игровые приставки",
        "playstation": "Игровые приставки",
        "xbox": "Игровые приставки",
        "монитор": "Мониторы",
        "аксессуар": "Аксессуары",
        "мышь": "Аксессуары",
        "клавиатура": "Аксессуары",
        "powerbank": "Аксессуары",
    }
    text = user_message.lower()
    found = set()
    for key, cat in mapping.items():
        if key in text:
            found.add(cat)
    return list(found)


def to_plain_dict(obj):
    """Рекурсивно преобразует все значения к простым типам."""
    if isinstance(obj, dict):
        return {str(k): to_plain_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_plain_dict(v) for v in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        return str(obj)


def get_products_id(products):
    """Генерирует уникальный ID для списка продуктов."""
    return hashlib.md5(str(sorted([p.id for p in products])).encode()).hexdigest()[:8]


def get_user_and_extra(message):
    """Получает пользователя и дополнительные данные."""
    session = SessionLocal()
    user = get_or_create_user(
        session, 
        message.from_user.id, 
        message.from_user.username, 
        message.from_user.first_name, 
        message.from_user.last_name
    )
    user_id = user.id
    extra = json.loads(user.extra_data) if user.extra_data else {}
    return session, user, user_id, extra


def save_user_data(session, user, extra):
    """Сохраняет данные пользователя."""
    user.extra_data = to_plain_dict(extra)
    session.commit()


def format_products_list(products):
    """Форматирует список продуктов."""
    if not products:
        return "К сожалению, товары не найдены."
    
    result = []
    for idx, product in enumerate(products, 1):
        result.append(f"{idx}. {product.name} — {product.price}₽\n{product.description}")
    
    return "\n\n".join(result)


def handle_errors(func):
    """Декоратор для обработки ошибок в обработчиках."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"[{func.__name__}] Ошибка: {e}")
            # Пропускаем неожиданные аргументы
            try:
                # Пытаемся вызвать функцию только с нужными аргументами
                if args:
                    return await func(args[0])  # Передаем только message
            except Exception:
                pass
    return wrapper


class MessageHandler:
    """Обработчик сообщений с современными паттернами проектирования."""
    
    def __init__(self):
        self.router = Router()
    
    def get_user_and_extra(self, message):
        """Получает пользователя и дополнительные данные."""
        return get_user_and_extra(message)
    
    def save_user_data(self, session, user, extra):
        """Сохраняет данные пользователя."""
        save_user_data(session, user, extra)
    
    def format_products_list(self, products):
        """Форматирует список продуктов."""
        return format_products_list(products) 