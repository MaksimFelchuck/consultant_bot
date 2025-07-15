from aiogram import Router, F
from aiogram.types import Message, InputFile, FSInputFile
from aiogram.filters import Command
from context import context_manager
from openai_api import get_gpt_response, get_category_by_llm
from database import SessionLocal
from database.service import (
    get_or_create_user, save_message, get_user_history, get_random_products_by_category, get_random_products_for_category
)
from context import format_products_for_context
from database.models import Category, Product, User
import re
from pathlib import Path
from sqlalchemy import func
from sqlalchemy import or_
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
import json
import logging

router = Router()

class OrderStates(StatesGroup):
    waiting_for_choice = State()
    waiting_for_contact = State()

BRAND_GROUPS = {
    "китайские": ["Xiaomi", "Realme", "Honor", "Huawei", "OnePlus", "Lenovo", "Meizu", "ZTE", "Vivo", "Oppo", "TCL", "Hisense"],
    "американские": ["Apple", "Google", "Microsoft", "Dell", "HP", "Sennheiser", "JBL", "Razer", "Kingston", "Baseus"],
    "корейские": ["Samsung", "LG"],
    "японские": ["Sony", "Panasonic", "Fujifilm", "Canon", "Nikon", "AOC"],
    "немецкие": ["Sennheiser"],
    "тайваньские": ["ASUS", "Acer", "MSI", "BenQ"],
    "швейцарские": ["Logitech"],
    "голландские": ["Philips"],
    "калифорнийские": ["Apple", "Google"],
}
SIZE_RANGES = {
    "телевизоры": {
        "маленький": ["43"],
        "средний": ["50", "55"],
        "большой": ["65", "75", "85"]
    },
    "ноутбуки": {
        "маленький": ["13"],
        "средний": ["14", "15.6"],
        "большой": ["16", "17"]
    },
    "мониторы": {
        "маленький": ["24"],
        "средний": ["27", "29"],
        "большой": ["32", "34", "49"]
    }
}
IGNORE_WORDS = ["не важно", "любой", "без разницы", "не имеет значения", "any", "doesn't matter", "посоветуй", "порекомендуй", "выбери"]

def get_category_by_keywords(user_message: str) -> list[str]:
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
    # Рекурсивно преобразует все значения к простым типам
    if isinstance(obj, dict):
        return {str(k): to_plain_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_plain_dict(v) for v in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        return str(obj)

@router.message(Command("start"))
async def cmd_start(message: Message):
    session = SessionLocal()
    categories = session.query(Category).all()
    session.close()
    cat_list = "\n".join([f"• {cat.name}" for cat in categories])
    # Картинка для ТехноМаркет (пример Unsplash)
    image_url = "images/hello_image.png"
    photo = FSInputFile(image_url)
    text = (
        "👋 Добро пожаловать в ТехноМаркет! 🛒\n\n"
        "Я — виртуальный помощник компании 🤖. Готов помочь с выбором техники, консультацией по товарам и оформлением заказа!\n\n"
        "В нашем магазине есть такие категории:\n"
        f"{cat_list}\n\n"
        "Что вас интересует? Пишите прямо сюда! 😊\n\n"
        "📦 Доставка по РФ | 💳 Оплата онлайн/наличными | 🛡️ Гарантия 1 год\n"
        "\nСайт: https://technomarket.ru\n\n"
        "⚠️ Внимание: бот тестовый, фото товаров не настоящие, заказы не обрабатываются."
    )
    await message.answer_photo(photo, caption=text)

@router.message(Command("setcontext"))
async def cmd_setcontext(message: Message):
    if message.text and len(message.text.split(maxsplit=1)) > 1:
        new_context = message.text.split(maxsplit=1)[1]
        context_manager.save_context(new_context)
        await message.answer("Контекст для консультаций обновлён! Теперь я буду учитывать новые инструкции от ТехноМаркет.")
    else:
        await message.answer("Пожалуйста, укажите новый контекст после команды. Например: /setcontext Вы консультант по бытовой технике.")

@router.message(Command("resetcontext"))
async def cmd_resetcontext(message: Message):
    context_manager.reset_context()
    await message.answer("Контекст сброшен к стандартному для ТехноМаркет. Я снова готов консультировать по товарам и услугам компании!")

@router.message(F.text)
async def handle_message(message: Message, state: FSMContext):
    user_message = message.text or ""
    session = SessionLocal()
    tg_user = message.from_user
    if tg_user is None:
        await message.answer("Ошибка: не удалось определить пользователя Telegram.")
        return
    user = get_or_create_user(
        session,
        telegram_id=str(tg_user.id),
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name
    )
    session.refresh(user)
    user_id = user.id if isinstance(user.id, int) else user.id.value
    save_message(session, user_id, "user", user_message)

    # Получаем историю для LLM
    history_limit = 5
    history = get_user_history(session, user_id, limit=history_limit)
    history_text = "\n".join([
        f"{m.role}: {m.message}" for m in history
    ])
    context = f"{context_manager.get_context()}\n\nИстория общения:\n{history_text}"
    reply = await get_gpt_response(user_message, context)
    save_message(session, user_id, "assistant", reply)

    # Парсим параметры поиска из ответа LLM
    search_params = None
    for line in reply.splitlines():
        if line.strip().lower().startswith("параметры поиска:"):
            search_params = line.strip()[len("Параметры поиска:"):].strip()
            break
    if search_params:
        # Пример: категория=Смартфоны, бренд=Samsung, цена=50000, характеристики=AMOLED
        params = {}
        for part in search_params.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                params[k.strip().lower()] = v.strip().lower()
        # Поиск товаров в базе
        query = session.query(Product)
        category_obj = None
        # Fallback: если нет категории — ищем в истории или в extra_data
        if ("категория" not in params or not params["категория"] or any(w in params["категория"] for w in IGNORE_WORDS)):
            # 1. Пробуем взять из last_category в extra_data
            extra = user.extra_data if isinstance(user.extra_data, dict) else {}
            if not isinstance(extra, dict):
                extra = {}
            last_category = extra.get("last_category")
            if last_category:
                params["категория"] = last_category
                logging.warning(f"[ТехноМаркет] LLM не указала категорию, используем last_category из extra_data: {last_category}")
            else:
                # 2. Пытаемся найти категорию в истории сообщений
                cat_from_history = get_category_by_keywords(history_text)
                if cat_from_history:
                    params["категория"] = cat_from_history[0]
                    extra["last_category"] = cat_from_history[0]
                    logging.warning(f"[ТехноМаркет] LLM не указала категорию, используем из истории: {cat_from_history[0]}")
                else:
                    logging.error("[ТехноМаркет] Не удалось определить категорию ни из параметров поиска, ни из истории!")
            user.extra_data = to_plain_dict(extra)  # type: ignore
            session.commit()
        if "категория" in params and not any(w in params["категория"] for w in IGNORE_WORDS):
            cat = session.query(Category).filter(Category.name.ilike(f"%{params['категория']}%"))
            category_obj = cat.first()
            if category_obj:
                query = query.filter(Product.category_id == category_obj.id)
                # Обновляем last_category в extra_data
                extra = user.extra_data if isinstance(user.extra_data, dict) else {}
                if not isinstance(extra, dict):
                    extra = {}
                extra["last_category"] = category_obj.name
                user.extra_data = to_plain_dict(extra)  # type: ignore
                session.commit()
        if "бренд" in params and not any(w in params["бренд"] for w in IGNORE_WORDS):
            brands = []
            # Проверяем группы брендов
            for group, group_brands in BRAND_GROUPS.items():
                if group in params["бренд"]:
                    brands.extend(group_brands)
            # Если явно указаны бренды через 'или', ',', '/'
            for b in re.split(r"[,/]| или | or ", params["бренд"]):
                b = b.strip()
                if b and b not in brands:
                    brands.append(b.capitalize())
            logging.info(f"[ТехноМаркет] Параметры поиска: {params}, бренды: {brands}")
            if brands:
                brand_filters = [Product.name.ilike(f"%{b}%") for b in brands]
                query = query.filter(or_(*brand_filters))
        if "цена" in params and not any(w in params["цена"] for w in IGNORE_WORDS):
            try:
                price = int(re.sub(r"\D", "", params["цена"]))
                query = query.filter(Product.price <= price)
            except Exception:
                pass
        # Обработка размера (маленький, средний, большой)
        if "характеристики" in params and not any(w in params["характеристики"] for w in IGNORE_WORDS):
            size_words = ["маленький", "средний", "большой"]
            for size_word in size_words:
                if size_word in params["характеристики"]:
                    # Определяем категорию для размера
                    cat_name = params.get("категория", "")
                    for key, ranges in SIZE_RANGES.items():
                        if key in cat_name.lower():
                            for sz in ranges[size_word]:
                                query = query.filter(Product.name.ilike(f"%{sz}%"))
                    break
            else:
                # Если нет слова "маленький/средний/большой", фильтруем по описанию
                query = query.filter(Product.description.ilike(f"%{params['характеристики']}%"))
        if "цвет" in params and not any(w in params["цвет"] for w in IGNORE_WORDS):
            # Разбиваем по 'или', ',', '/'
            colors = [c.strip() for c in re.split(r"[,/]| или | or ", params["цвет"]) if c.strip()]
            if colors:
                color_filters = [or_(Product.name.ilike(f"%{color}%"), Product.description.ilike(f"%{color}%")) for color in colors]
                query = query.filter(or_(*color_filters))
        products = query.order_by(func.random()).limit(3).all()
        # Fallback: если не найдено, но есть категория — показать случайные товары из категории
        if not products and category_obj:
            # Не предлагаем альтернативы без пояснения — только если LLM явно объяснила, что это альтернатива
            pass
        if products:
            text_lines = [reply.split("Параметры поиска:")[0].strip()]
            for idx, prod in enumerate(products, 1):
                text_lines.append(f"{idx}. {prod.name} — {prod.price}₽\n{prod.description}")
            text_lines.append("\nЕсли хотите посмотреть фото товара — напишите 'фото' и номер или название товара.")
            await message.answer("\n\n".join(text_lines))
            # Сохраняем последние товары для выбора
            extra = user.extra_data if isinstance(user.extra_data, dict) else {}
            if not isinstance(extra, dict):
                extra = {}
            # Готовим last_products только из простых типов
            last_products = []
            for p in products:
                price_val = getattr(p, 'price', 0)
                try:
                    price_val = int(price_val)
                except Exception:
                    price_val = 0
                last_products.append({
                    "name": str(getattr(p, 'name', '')),
                    "image_url": str(getattr(p, 'image_url', '')),
                    "desc": str(getattr(p, 'description', '')),
                    "price": price_val
                })
            extra["last_products"] = last_products
            user.extra_data = to_plain_dict(extra)  # type: ignore
            session.commit()
            await state.set_state(OrderStates.waiting_for_choice)
        else:
            await message.answer(reply.split("Параметры поиска:")[0].strip() + "\n\nНе удалось найти подходящие товары по вашему запросу.")
    else:
        await message.answer(reply)
    session.close()

# Обработка запроса фото товара
@router.message(F.text.regexp(r"(?i)фото|картинка|photo|picture"))
async def handle_photo_request(message: Message, state: FSMContext):
    user_message = message.text or ""
    session = SessionLocal()
    tg_user = message.from_user
    if tg_user is None:
        await message.answer("Ошибка: не удалось определить пользователя Telegram.")
        return
    user = get_or_create_user(
        session,
        telegram_id=str(tg_user.id),
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name
    )
    session.refresh(user)
    extra = user.extra_data if isinstance(user.extra_data, dict) else {}
    if not isinstance(extra, dict):
        extra = {}
    last_products = extra.get("last_products", [])
    # Пытаемся найти номер или название товара в сообщении
    choice = user_message.lower()
    chosen = None
    # По номеру
    for idx, prod in enumerate(last_products, 1):
        if str(idx) in choice:
            chosen = prod
            break
    # По названию
    if not chosen:
        for prod in last_products:
            if prod["name"].lower() in choice:
                chosen = prod
                break
    if chosen:
        if chosen["image_url"].startswith("images/"):
            file_path = Path(chosen["image_url"]).resolve()
            photo = FSInputFile(str(file_path))
            await message.answer_photo(photo, caption=chosen["name"])
        else:
            await message.answer_photo(chosen["image_url"], caption=chosen["name"])
    else:
        await message.answer("Не удалось определить, для какого товара показать фото. Пожалуйста, укажите номер или точное название товара из последней выдачи.")
    session.close() 