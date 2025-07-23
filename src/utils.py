"""
Утилитарные функции для бота ТехноМаркет.
"""

import hashlib
import json
import logging
import re
from constants import IgnoreWords
from pathlib import Path

from aiogram import Router
from aiogram.types import Message

from database import SessionLocal
from database.models import Product
from repository import user_repo


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
    user = user_repo.get_or_create(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    )
    user_id = user.id
    extra = user.extra_data if user.extra_data else {}
    return None, user, user_id, extra


def save_user_data(session, user, extra):
    """Сохраняет данные пользователя."""
    user_repo.update_extra_data(user, to_plain_dict(extra))


def format_products_list(products):
    """Форматирует список продуктов."""
    if not products:
        return "К сожалению, товары не найдены."

    result = []
    for idx, product in enumerate(products, 1):
        result.append(
            f"{idx}. {product.name} — {product.price}₽\n{product.description}"
        )

    return "\n\n".join(result)


def handle_errors(func):
    """Декоратор для обработки ошибок в обработчиках."""

    async def wrapper(*args, **kwargs):
        try:
            # Фильтруем kwargs, оставляя только те, которые принимает функция
            import inspect

            sig = inspect.signature(func)
            valid_kwargs = {}

            for param_name, param in sig.parameters.items():
                if param_name in kwargs:
                    valid_kwargs[param_name] = kwargs[param_name]

            return await func(*args, **valid_kwargs)
        except Exception as e:
            logging.error(f"[{func.__name__}] Ошибка: {e}")
            # Можно добавить отправку сообщения пользователю об ошибке
            if args and hasattr(args[0], "answer"):
                try:
                    await args[0].answer("Произошла ошибка. Попробуйте еще раз.")
                except:
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


def parse_search_params_from_ai_response(reply, saved_params):
    """Парсит параметры поиска из ответа ИИ."""
    search_params = None
    for line in reply.splitlines():
        if line.strip().lower().startswith("параметры поиска:"):
            search_params = line.strip()[len("параметры поиска:") :].strip()
            break

    params = dict(saved_params) if saved_params else {}
    if search_params:
        for part in search_params.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                k = k.strip().lower()
                v = v.strip().lower()
                if v and v not in IgnoreWords.WORDS:
                    params[k] = v

    return params


# def process_category_logic(params, extra, history_text):
#     """Обрабатывает логику определения категории товара."""
#     if (
#         "категория" not in params
#         or not params["категория"]
#         or any(w in params["категория"] for w in IgnoreWords.WORDS)
#     ):
#         last_category = extra.get("last_category")
#         if last_category:
#             params["категория"] = last_category
#         else:
#             cat_from_history = get_category_by_keywords(history_text)
#             if cat_from_history:
#                 params["категория"] = cat_from_history[0]
#                 extra["last_category"] = cat_from_history[0]

#     category_obj = None
#     if "категория" in params and not any(
#         w in params["категория"] for w in IgnoreWords.WORDS
#     ):
#         from repository import category_repo

#         category_obj = category_repo.get_by_name(params["категория"])
#         if category_obj:
#             extra["last_category"] = category_obj.name

#     return params, extra, category_obj


def build_search_filters(params):
    """Строит фильтры для поиска товаров на основе параметров."""
    from database.models import Product
    from sqlalchemy import or_
    from constants import BrandGroups, SizeRanges

    filters = {"color": [], "brand": [], "spec": [], "price": []}

    if "цвет" in params and not any(w in params["цвет"] for w in IgnoreWords.WORDS):
        colors = [
            c.strip() for c in re.split(r"[,/]| или | or ", params["цвет"]) if c.strip()
        ]
        if colors:
            filters["color"] = [
                or_(
                    Product.name.ilike(f"%{color}%"),
                    Product.description.ilike(f"%{color}%"),
                )
                for color in colors
            ]

    if "бренд" in params and not any(w in params["бренд"] for w in IgnoreWords.WORDS):
        brands = []
        for group, group_brands in BrandGroups.get_all_brands().items():
            if group in params["бренд"]:
                brands.extend(group_brands)
        for b in re.split(r"[,/]| или | or ", params["бренд"]):
            b = b.strip()
            if b and b not in brands:
                brands.append(b.capitalize())
        if brands:
            filters["brand"] = [Product.name.ilike(f"%{b}%") for b in brands]

    if "характеристики" in params and not any(
        w in params["характеристики"] for w in IgnoreWords.WORDS
    ):
        size_words = ["маленький", "средний", "большой"]
        for size_word in size_words:
            if size_word in params["характеристики"]:
                cat_name = params.get("категория", "")
                for key, ranges in SizeRanges.get_all_ranges().items():
                    if key in cat_name.lower():
                        for sz in ranges[size_word]:
                            filters["spec"].append(Product.name.ilike(f"%{sz}%"))
                break
        else:
            filters["spec"].append(
                Product.description.ilike(f"%{params['характеристики']}%")
            )

    if "тип" in params and not any(w in params["тип"] for w in IgnoreWords.WORDS):
        filters["spec"].append(Product.name.ilike(f"%{params['тип']}%"))
        filters["spec"].append(Product.description.ilike(f"%{params['тип']}%"))

    if "цена" in params and not any(w in params["цена"] for w in IgnoreWords.WORDS):
        try:
            price = int(re.sub(r"\D", "", params["цена"]))
            filters["price"] = [Product.price <= price]
        except Exception:
            pass

    return filters


def clean_ai_response(response):
    """Очищает ответ ИИ от технических строк."""
    cleaned_response = "\n".join(
        line
        for line in response.splitlines()
        if not (
            line.strip().lower().startswith("параметры поиска:")
            or line.strip().lower().startswith("извлечённые параметры:")
        )
    ).strip()

    return cleaned_response
