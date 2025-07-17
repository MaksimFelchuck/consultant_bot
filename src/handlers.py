from aiogram import Router, F
from aiogram.types import Message, FSInputFile
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
import hashlib
from typing import Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session

router = Router()

class OrderStates(StatesGroup):
    waiting_for_choice = State()
    waiting_for_contact = State()
    product_card = State()  # Новое состояние для карточки товара

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

def get_products_id(products):
    return hashlib.md5(json.dumps(products, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

# --- Константы сообщений ---
USER_NOT_FOUND_MSG = "Ошибка: не удалось определить пользователя Telegram."
TECHNICAL_ERROR_MSG = "Произошла техническая ошибка. Пожалуйста, попробуйте ещё раз или переформулируйте запрос. Если проблема повторяется, напишите: 'помощь'."
PHOTO_ERROR_MSG = "Произошла техническая ошибка при попытке показать фото. Попробуйте ещё раз или выберите другой товар."
CHOICE_ERROR_MSG = "Произошла техническая ошибка при выборе товара. Пожалуйста, попробуйте ещё раз или выберите другой товар."
CARD_ERROR_MSG = "Произошла техническая ошибка при обработке информации о товаре. Пожалуйста, попробуйте ещё раз или выберите другой товар."
CONTEXT_UPDATED_MSG = "Контекст для консультаций обновлён! Теперь я буду учитывать новые инструкции от ТехноМаркет."
CONTEXT_PROMPT_MSG = "Пожалуйста, укажите новый контекст после команды. Например: /setcontext Вы консультант по бытовой технике."
CONTEXT_RESET_MSG = "Контекст сброшен к стандартному для ТехноМаркет. Я снова готов консультировать по товарам и услугам компании!"
PHOTO_NOT_FOUND_MSG = "Фото товара {name} временно недоступно."
PRODUCT_NOT_FOUND_MSG = "Извините, не удалось найти информацию о выбранном товаре. Попробуйте выбрать товар заново или уточните ваш запрос. Например: 'покажи список телефонов', 'покажи Samsung'."
CHOOSE_ANOTHER_MSG = "Возвращаюсь к списку товаров. Выберите другой товар или уточните параметры поиска."
NO_ANSWER_MSG = "Извините, я не смог найти ответ на ваш вопрос. Пожалуйста, уточните, что именно вас интересует, или попробуйте переформулировать запрос. Например: 'характеристики', 'цена', 'фото'."

def handle_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            await args[0].answer(str(e))
        except Exception as e:
            import logging
            logging.error(f"[{func.__name__}] Ошибка: {e}")
            await args[0].answer(TECHNICAL_ERROR_MSG)
    return wrapper

def get_user_and_extra(message: Message) -> Tuple[Session, 'User', int, dict]:
    session = SessionLocal()
    tg_user = message.from_user
    if tg_user is None:
        session.close()
        raise ValueError(USER_NOT_FOUND_MSG)
    user = get_or_create_user(
        session,
        telegram_id=str(tg_user.id),
        username=tg_user.username,
        first_name=tg_user.first_name,
        last_name=tg_user.last_name
    )
    session.refresh(user)
    user_id = user.id
    if hasattr(user_id, 'value'):
        user_id = user_id.value
    if not isinstance(user_id, int):
        user_id = int(user_id)
    extra = user.extra_data if isinstance(user.extra_data, dict) else {}
    if not isinstance(extra, dict):
        extra = {}
    return session, user, user_id, extra

@dataclass
class ProductCard:
    name: str
    image_url: str
    desc: str
    price: int

def format_product_card(card: ProductCard) -> str:
    return f"{card.name} — {card.price}₽\n{card.desc}"

def format_products_list(products: list[ProductCard]) -> str:
    return "\n\n".join(
        f"{idx+1}. {format_product_card(p)}" for idx, p in enumerate(products)
    )

@router.message(Command("start"))
@handle_errors
async def cmd_start(message: Message):
    session, user, user_id, extra = get_user_and_extra(message)
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
        "Что вас интересует? Пишите прямо сюда! \n\n"
        "📦 Доставка по РФ | �� Оплата онлайн/наличными | 🛡️ Гарантия 1 год\n"
        "\nСайт: https://technomarket.ru\n\n"
        "⚠️ Внимание: бот тестовый, фото товаров не настоящие, заказы не обрабатываются."
    )
    await message.answer_photo(photo, caption=text)

@router.message(Command("setcontext"))
@handle_errors
async def cmd_setcontext(message: Message):
    if message.text and len(message.text.split(maxsplit=1)) > 1:
        new_context = message.text.split(maxsplit=1)[1]
        context_manager.save_context(new_context)
        await message.answer(CONTEXT_UPDATED_MSG)
    else:
        await message.answer(CONTEXT_PROMPT_MSG)

@router.message(Command("resetcontext"))
@handle_errors
async def cmd_resetcontext(message: Message):
    context_manager.reset_context()
    await message.answer(CONTEXT_RESET_MSG)

@router.message(F.text)
@handle_errors
async def handle_message(message: Message, state: FSMContext):
    # Проверяем текущее состояние FSM
    current_state = await state.get_state()
    if current_state:
        return  # Пусть обработку делает соответствующий handler
    user_message = message.text or ""
    session, user, user_id, extra = get_user_and_extra(message)
    save_message(session, user_id, "user", user_message)
    # Получаем историю для LLM
    history_limit = 5
    history = get_user_history(session, user_id, limit=history_limit)
    history_text = "\n".join([
        f"{m.role}: {m.message}" for m in history
    ])
    # --- Сохраняем и объединяем параметры пользователя ---
    saved_params = extra.get("search_params", {})
    context = f"{context_manager.get_context()}\n\nИстория общения:\n{history_text}"
    reply = await get_gpt_response(user_message, context)
    save_message(session, user_id, "assistant", reply)
    # Парсим параметры поиска из ответа LLM
    search_params = None
    for line in reply.splitlines():
        if line.strip().lower().startswith("параметры поиска:"):
            search_params = line.strip()[len("Параметры поиска:"):].strip()
            break
    # --- Объединяем новые параметры с сохранёнными ---
    params = dict(saved_params) if saved_params else {}
    if search_params:
        for part in search_params.split(","):
            if "=" in part:
                k, v = part.split("=", 1)
                k = k.strip().lower()
                v = v.strip().lower()
                if v and v not in IGNORE_WORDS:
                    params[k] = v
    # Сохраняем объединённые параметры
    extra["search_params"] = params
    user.extra_data = to_plain_dict(extra)  # type: ignore
    session.commit()
    # Проверка наличия хотя бы одной характеристики (только если это первое сообщение)
    KEY_PARAMS = ["цена", "бюджет", "бренд", "цвет", "характеристики", "размер", "модель", "объём", "оперативная память", "экран", "тип"]
    has_characteristics = any(
        k in params and params[k] and params[k] not in IGNORE_WORDS
        for k in KEY_PARAMS
    )
    if not has_characteristics:
        # Удаляем все технические строки из ответа LLM перед отправкой пользователю
        cleaned_reply = "\n".join(
            line for line in reply.splitlines()
            if not (line.strip().lower().startswith("параметры поиска:") or 
                   line.strip().lower().startswith("извлечённые параметры:"))
        ).strip()
        if cleaned_reply:
            await message.answer(cleaned_reply)
        session.close()
        return
    # Поиск товаров в базе
    query = session.query(Product)
    category_obj = None
    # Fallback: если нет категории — ищем в истории или в extra_data
    if ("категория" not in params or not params["категория"] or any(w in params["категория"] for w in IGNORE_WORDS)):
        last_category = extra.get("last_category")
        if last_category:
            params["категория"] = last_category
            logging.warning(f"[ТехноМаркет] LLM не указала категорию, используем last_category из extra_data: {last_category}")
        else:
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
            extra["last_category"] = category_obj.name
            user.extra_data = to_plain_dict(extra)  # type: ignore
            session.commit()
    # --- Сбор фильтров ---
    filters = {'color': [], 'brand': [], 'spec': [], 'price': []}
    if "цвет" in params and not any(w in params["цвет"] for w in IGNORE_WORDS):
        colors = [c.strip() for c in re.split(r"[,/]| или | or ", params["цвет"]) if c.strip()]
        if colors:
            filters['color'] = [or_(Product.name.ilike(f"%{color}%"), Product.description.ilike(f"%{color}%")) for color in colors]
    if "бренд" in params and not any(w in params["бренд"] for w in IGNORE_WORDS):
        brands = []
        for group, group_brands in BRAND_GROUPS.items():
            if group in params["бренд"]:
                brands.extend(group_brands)
        for b in re.split(r"[,/]| или | or ", params["бренд"]):
            b = b.strip()
            if b and b not in brands:
                brands.append(b.capitalize())
        if brands:
            filters['brand'] = [Product.name.ilike(f"%{b}%") for b in brands]
    if "характеристики" in params and not any(w in params["характеристики"] for w in IGNORE_WORDS):
        size_words = ["маленький", "средний", "большой"]
        for size_word in size_words:
            if size_word in params["характеристики"]:
                cat_name = params.get("категория", "")
                for key, ranges in SIZE_RANGES.items():
                    if key in cat_name.lower():
                        for sz in ranges[size_word]:
                            filters['spec'].append(Product.name.ilike(f"%{sz}%"))
                break
        else:
            filters['spec'].append(Product.description.ilike(f"%{params['характеристики']}%"))
    # --- Новый фильтр по типу (проводные/беспроводные) ---
    if "тип" in params and not any(w in params["тип"] for w in IGNORE_WORDS):
        filters['spec'].append(Product.name.ilike(f"%{params['тип']}%"))
        filters['spec'].append(Product.description.ilike(f"%{params['тип']}%"))
    if "цена" in params and not any(w in params["цена"] for w in IGNORE_WORDS):
        try:
            price = int(re.sub(r"\D", "", params["цена"]))
            filters['price'] = [Product.price <= price]
        except Exception:
            pass
    # --- Поиск товаров с поэтапным ослаблением фильтров ---
    def smart_product_search(query, filters, session, category_obj):
        q = query
        if filters['color']:
            q = q.filter(or_(*filters['color']))
        if filters['brand']:
            q = q.filter(or_(*filters['brand']))
        if filters['spec']:
            q = q.filter(*filters['spec'])
        if filters['price']:
            q = q.filter(*filters['price'])
        products = q.order_by(func.random()).limit(3).all()
        if products:
            return products, []
        q = query
        if filters['brand']:
            q = q.filter(or_(*filters['brand']))
        if filters['spec']:
            q = q.filter(*filters['spec'])
        if filters['price']:
            q = q.filter(*filters['price'])
        products = q.order_by(func.random()).limit(3).all()
        if products:
            return products, ['цвет']
        q = query
        if filters['spec']:
            q = q.filter(*filters['spec'])
        if filters['price']:
            q = q.filter(*filters['price'])
        products = q.order_by(func.random()).limit(3).all()
        if products:
            return products, ['цвет', 'бренд']
        q = query
        if filters['price']:
            q = q.filter(*filters['price'])
        products = q.order_by(func.random()).limit(3).all()
        if products:
            return products, ['цвет', 'бренд', 'характеристики']
        if filters['price']:
            q = session.query(Product).filter(Product.category_id == category_obj.id).filter(*filters['price'])
        else:
            q = session.query(Product).filter(Product.category_id == category_obj.id)
        products = q.order_by(func.random()).limit(3).all()
        if products:
            return products, ['цвет', 'бренд', 'характеристики', 'категория']
        products = session.query(Product).filter(Product.category_id == category_obj.id).order_by(func.random()).limit(3).all()
        return products, ['все фильтры']
    products, dropped = smart_product_search(query, filters, session, category_obj)
    main_text = reply.split("Параметры поиска:")[0].strip()
    # Удаляем все технические строки из main_text
    main_text = "\n".join(
        line for line in main_text.splitlines()
        if not (line.strip().lower().startswith("параметры поиска:") or 
               line.strip().lower().startswith("извлечённые параметры:"))
    ).strip()
    # --- Обработка зависания/непонятного запроса ---
    if not main_text and not products:
        await message.answer(
            "Извините, я не совсем понял ваш запрос. Пожалуйста, уточните, какой товар вас интересует, например: 'покажи первый айфон' или 'расскажи подробнее про iPhone 15 Pro'."
        )
        session.close()
        return
    if dropped:
        # Новая логика: если среди dropped есть 'цвет' и пользователь явно указывал цвет
        if 'цвет' in dropped and 'цвет' in params and params['цвет']:
            color = params['цвет']
            msg = f"{color.capitalize()} айфон не нашёл, но могу предложить такие айфоны:"
        else:
            msg = "По вашему запросу ничего не найдено, но вот несколько товаров из этой категории, которые могут вам подойти:"
        await message.answer(msg)
        main_text = ""
    # --- Обработка случая, когда не найдено ни одного товара даже после ослабления всех фильтров ---
    if not products:
        await message.answer(
            "К сожалению, подходящих товаров не нашлось. Если хотите, помогу подобрать что-то похожее — просто напишите, что для вас важно, или попробуйте изменить запрос!"
        )
        session.close()
        return
    if products:
        text_lines = [main_text] if main_text else []
        for idx, prod in enumerate(products, 1):
            text_lines.append(f"{idx}. {prod.name} — {prod.price}₽\n{prod.description}")
        category_name = category_obj.name if category_obj and hasattr(category_obj, 'name') else "товар"
        text_lines.append(f"\nЕсли какой-то {category_name.lower()} вас заинтересовал, введите его номер или название, чтобы узнать подробности и увидеть фото.")
        await message.answer("\n\n".join(text_lines))
        # Сохраняем последние товары для выбора
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
        extra["current_product_list_id"] = get_products_id(last_products)
        user.extra_data = to_plain_dict(extra)  # type: ignore
        session.commit()
        await state.set_state(OrderStates.waiting_for_choice)
    session.close()

# Обработка запроса фото товара
@router.message(F.text.regexp(r"(?i)фото|картинка|photo|picture|покажи|show"))
@handle_errors
async def handle_any_photo_request(message: Message, state: FSMContext):
    """Обрабатывает запрос фото в любом состоянии: всегда отправляет реальное фото по image_url"""
    user_message = message.text or ""
    session, user, _, extra = get_user_and_extra(message)
    # Сначала ищем current_product (выбранный товар)
    chosen = extra.get("current_product")
    # Если нет — берём первый из last_products
    if not chosen:
        last_products = extra.get("last_products", [])
        if last_products:
            chosen = last_products[0]
    if chosen and "image_url" in chosen:
        await message.answer_photo(chosen["image_url"], caption=chosen.get("name", "Фото товара"))
    else:
        await message.answer("Не удалось определить, для какого товара показать фото. Пожалуйста, выберите товар из последней выдачи или уточните, что вы хотите увидеть. Например: 'покажи фото первого телефона', 'покажи фото Samsung'.")
    session.close()

@router.message(StateFilter(OrderStates.waiting_for_choice), F.text)
@handle_errors
async def handle_product_choice(message: Message, state: FSMContext):
    user_message = message.text or ""
    session, user, user_id, extra = get_user_and_extra(message)
    last_products = extra.get("last_products", [])
    last_products_id = get_products_id(last_products) if last_products else None
    current_products_id = extra.get("current_product_list_id")
    choice = user_message.lower()
    chosen = None
    # По номеру
    for idx, prod in enumerate(last_products, 1):
        if str(idx) == choice.strip():
            chosen = prod
            break
    # По названию (частичное совпадение)
    if not chosen:
        for prod in last_products:
            if prod["name"].lower() in choice or choice in prod["name"].lower():
                chosen = prod
                break
    if chosen:
        from aiogram.types import FSInputFile
        file_path = Path.cwd() / chosen["image_url"]
        if file_path.exists():
            photo = FSInputFile(str(file_path))
            caption = f"{chosen['name']} — {chosen['price']}₽\n{chosen['desc']}"
            await message.answer_photo(photo, caption=caption + "\n\nХотите оформить заказ на этот товар? Напишите 'оформить заказ' или свяжитесь с менеджером.")
        else:
            await message.answer(f"{chosen['name']}\nФото не найдено.\n{chosen['desc']}")
        # Сохраняем выбранный товар и переходим в состояние карточки товара
        extra["current_product"] = chosen
        extra["current_product_list_id"] = last_products_id
        user.extra_data = to_plain_dict(extra)  # type: ignore
        session.commit()
        await state.set_state(OrderStates.product_card)
    else:
        await message.answer("Не удалось определить, какой товар вы выбрали. Пожалуйста, введите номер или точное название товара из последней выдачи или уточните ваш запрос. Например: 'покажи первый', 'покажи Samsung'.")
    session.close()

@router.message(StateFilter(OrderStates.product_card), F.text)
@handle_errors
async def handle_product_card(message: Message, state: FSMContext):
    """Обработчик для состояния карточки товара - отвечает на вопросы о выбранном товаре"""
    user_message = message.text or ""
    session, user, _, extra = get_user_and_extra(message)
    current_product = extra.get("current_product")
    
    if not current_product:
        await message.answer(PRODUCT_NOT_FOUND_MSG)
        await state.clear()
        session.close()
        return
    
    # Обработка различных запросов в карточке товара
    user_message_lower = user_message.lower()
    
    # Запрос фото
    if any(word in user_message_lower for word in ["фото", "картинка", "photo", "picture", "покажи", "show"]):
        if current_product["image_url"].startswith("images/"):
            from aiogram.types import FSInputFile
            file_path = Path.cwd() / current_product["image_url"]
            if file_path.exists():
                photo = FSInputFile(str(file_path))
                await message.answer_photo(photo, caption=current_product["name"])
            else:
                await message.answer(PHOTO_NOT_FOUND_MSG.format(name=current_product["name"]))
        else:
            await message.answer_photo(current_product["image_url"], caption=current_product["name"])
    
    # Запрос характеристик
    elif any(word in user_message_lower for word in ["характеристики", "характеристика", "описание", "подробности", "детали", "specs", "specifications"]):
        await message.answer(f"📋 Характеристики {current_product['name']}:\n\n{current_product['desc']}\n\n💰 Цена: {current_product['price']}₽")
    
    # Запрос цены
    elif any(word in user_message_lower for word in ["цена", "стоимость", "price", "cost", "сколько стоит"]):
        await message.answer(f"💰 Цена {current_product['name']}: {current_product['price']}₽")
    
    # Оформление заказа
    elif any(word in user_message_lower for word in ["заказ", "купить", "приобрести", "оформить", "order", "buy", "purchase"]):
        await message.answer(
            f"🛒 Оформление заказа на {current_product['name']}\n\n"
            f"Для оформления заказа свяжитесь с нашим менеджером:\n"
            f"📞 Телефон: +7 (800) 555-0123\n"
            f"�� Email: order@technomarket.ru\n"
            f"💬 Telegram: @technomarket_support\n\n"
            f"Или оставьте свой номер телефона, и мы перезвоним вам в течение 15 минут."
        )
        await state.set_state(OrderStates.waiting_for_contact)
    
    # Возврат к списку товаров
    elif any(word in user_message_lower for word in ["назад", "список", "другие", "еще", "back", "list", "other", "more"]):
        await message.answer(CHOOSE_ANOTHER_MSG)
        await state.clear()
    
    # Общие вопросы о товаре
    else:
        # Используем LLM для ответов на вопросы о конкретном товаре
        context = f"""Ты — консультант магазина "ТехноМаркет". Пользователь задает вопрос о товаре:

Товар: {current_product['name']}
Описание: {current_product['desc']}
Цена: {current_product['price']}₽

Вопрос пользователя: {user_message}

Отвечай кратко и по делу. Если пользователь спрашивает о характеристиках, которые не указаны в описании, вежливо сообщи, что эта информация временно недоступна и предложи связаться с менеджером для уточнения деталей."""
        
        reply = await get_gpt_response(user_message, context)
        if not reply or not reply.strip():
            await message.answer(NO_ANSWER_MSG)
        else:
            await message.answer(reply)
    
    session.close() 