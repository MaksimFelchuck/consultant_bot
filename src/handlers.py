"""
Обработчики сообщений для бота ТехноМаркет.
"""

import json
import re
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message
from sqlalchemy import or_

from constants import BrandGroups, IgnoreWords, Messages, SizeRanges
from context import context_manager
from openai_api import get_gpt_response
from repository import (
    category_repo,
    message_repo,
    product_repo,
    search_service,
    user_repo,
)
from utils import (
    format_products_list,
    get_category_by_keywords,
    get_products_id,
    handle_errors,
)

router = Router()


class OrderStates(StatesGroup):
    waiting_for_choice = State()
    waiting_for_contact = State()
    product_card = State()


@router.message(Command("start"))
@handle_errors
async def cmd_start(message: Message):
    categories = category_repo.get_all()
    cat_list = "\n".join([f"• {cat.name}" for cat in categories])
    image_url = "images/hello_image.png"
    photo = FSInputFile(image_url)
    text = (
        "👋 Добро пожаловать в ТехноМаркет! 🛒\n\n"
        "Я — виртуальный помощник компании 🤖. Готов помочь с выбором техники, консультацией по товарам и оформлением заказа!\n\n"
        "В нашем магазине есть такие категории:\n"
        f"{cat_list}\n\n"
        "Что вас интересует? Пишите прямо сюда! \n\n"
        "📦 Доставка по РФ | 💳 Оплата онлайн/наличными | 🛡️ Гарантия 1 год\n"
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
        await message.answer(Messages.CONTEXT_UPDATED)
    else:
        await message.answer(Messages.CONTEXT_PROMPT)


@router.message(Command("resetcontext"))
@handle_errors
async def cmd_resetcontext(message: Message):
    context_manager.reset_context()
    await message.answer(Messages.CONTEXT_RESET)


@router.message(F.text)
async def handle_message(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        return

    user_message = message.text or ""

    user = user_repo.get_or_create(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    )
    user_id = user.id
    extra = json.loads(user.extra_data) if user.extra_data else {}

    message_repo.save_message(user_id, "user", user_message)

    history_limit = 5
    history = message_repo.get_user_history(user_id, limit=history_limit)
    history_text = "\n".join([f"{m.role}: {m.message}" for m in history])

    saved_params = extra.get("search_params", {})
    context = f"{context_manager.get_context()}\n\nИстория общения:\n{history_text}"
    reply = await get_gpt_response(user_message, context)
    message_repo.save_message(user_id, "assistant", reply)

    search_params = None
    for line in reply.splitlines():
        if line.strip().lower().startswith("параметры поиска:"):
            search_params = line.strip()[len("Параметры поиска:") :].strip()
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

    extra["search_params"] = params
    user_repo.update_extra_data(user, extra)

    KEY_PARAMS = [
        "цена",
        "бюджет",
        "бренд",
        "цвет",
        "характеристики",
        "размер",
        "модель",
        "объём",
        "оперативная память",
        "экран",
        "тип",
    ]
    has_characteristics = any(
        k in params and params[k] and params[k] not in IgnoreWords.WORDS
        for k in KEY_PARAMS
    )

    if not has_characteristics:
        cleaned_reply = "\n".join(
            line
            for line in reply.splitlines()
            if not (
                line.strip().lower().startswith("параметры поиска:")
                or line.strip().lower().startswith("извлечённые параметры:")
            )
        ).strip()
        if cleaned_reply:
            await message.answer(cleaned_reply)
        return

    category_obj = None

    if (
        "категория" not in params
        or not params["категория"]
        or any(w in params["категория"] for w in IgnoreWords.WORDS)
    ):
        last_category = extra.get("last_category")
        if last_category:
            params["категория"] = last_category
        else:
            cat_from_history = get_category_by_keywords(history_text)
            if cat_from_history:
                params["категория"] = cat_from_history[0]
                extra["last_category"] = cat_from_history[0]

    if "категория" in params and not any(
        w in params["категория"] for w in IgnoreWords.WORDS
    ):
        category_obj = category_repo.get_by_name(params["категория"])
        if category_obj:
            extra["last_category"] = category_obj.name
            user_repo.update_extra_data(user, extra)

    filters = {"color": [], "brand": [], "spec": [], "price": []}

    if "цвет" in params and not any(w in params["цвет"] for w in IgnoreWords.WORDS):
        colors = [
            c.strip() for c in re.split(r"[,/]| или | or ", params["цвет"]) if c.strip()
        ]
        if colors:
            from database.models import Product

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
            from database.models import Product

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
                            from database.models import Product

                            filters["spec"].append(Product.name.ilike(f"%{sz}%"))
                break
        else:
            from database.models import Product

            filters["spec"].append(
                Product.description.ilike(f"%{params['характеристики']}%")
            )

    if "тип" in params and not any(w in params["тип"] for w in IgnoreWords.WORDS):
        from database.models import Product

        filters["spec"].append(Product.name.ilike(f"%{params['тип']}%"))
        filters["spec"].append(Product.description.ilike(f"%{params['тип']}%"))

    if "цена" in params and not any(w in params["цена"] for w in IgnoreWords.WORDS):
        try:
            price = int(re.sub(r"\D", "", params["цена"]))
            from database.models import Product

            filters["price"] = [Product.price <= price]
        except Exception:
            pass

    category_id = category_obj.id if category_obj else None
    products, dropped_filters = search_service.smart_search(category_id, filters)

    if products:
        products_id = get_products_id(products)
        extra["last_products"] = [
            {
                "id": p.id,
                "name": p.name,
                "image_url": p.image_url,
                "desc": p.description,
                "price": p.price,
            }
            for p in products
        ]
        extra["last_products_id"] = products_id
        user_repo.update_extra_data(user, extra)

        products_text = format_products_list(products)

        if dropped_filters:
            dropped_text = f"\n\n⚠️ Не удалось найти товары со всеми параметрами. Игнорированы: {', '.join(dropped_filters)}"
            products_text += dropped_text

        await message.answer(
            products_text
            + "\n\nЕсли товар вас заинтересовал, введите его номер или название для получения подробной информации."
        )
        await state.set_state(OrderStates.waiting_for_choice)
    else:
        context = f"{context_manager.get_context()}\n\nИстория общения:\n{history_text}\n\nПараметры поиска: {params}"
        fallback_reply = await get_gpt_response(user_message, context)
        message_repo.save_message(user_id, "assistant", fallback_reply)

        cleaned_fallback = "\n".join(
            line
            for line in fallback_reply.splitlines()
            if not (
                line.strip().lower().startswith("параметры поиска:")
                or line.strip().lower().startswith("извлечённые параметры:")
            )
        ).strip()

        if cleaned_fallback:
            await message.answer(cleaned_fallback)
        else:
            await message.answer(
                "К сожалению, не удалось найти подходящие товары. Попробуйте изменить параметры поиска."
            )


@router.message(F.text.regexp(r"(?i)фото|картинка|photo|picture|покажи|show"))
async def handle_any_photo_request(message: Message, state: FSMContext):
    user_message = message.text or ""
    user = user_repo.get_or_create(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    )
    extra = json.loads(user.extra_data) if user.extra_data else {}

    last_products = extra.get("last_products", [])
    if not last_products:
        await message.answer(
            "Сначала найдите товары, а затем запросите фото конкретного товара."
        )
        return

    choice = re.sub(
        r"(?i)фото|картинка|photo|picture|покажи|show", "", user_message
    ).strip()
    if not choice:
        await message.answer(
            "Укажите номер или название товара, фото которого хотите увидеть."
        )
        return

    chosen = None
    try:
        num = int(choice)
        if 1 <= num <= len(last_products):
            chosen = last_products[num - 1]
    except ValueError:
        pass

    if not chosen:
        for prod in last_products:
            if prod["name"].lower() in choice or choice in prod["name"].lower():
                chosen = prod
                break

    if chosen:
        file_path = Path.cwd() / chosen["image_url"]
        if file_path.exists():
            photo = FSInputFile(str(file_path))
            caption = f"{chosen['name']} — {chosen['price']}₽\n{chosen['desc']}"
            await message.answer_photo(
                photo,
                caption=caption
                + "\n\nХотите оформить заказ на этот товар? Напишите 'оформить заказ' или свяжитесь с менеджером.",
            )
        else:
            await message.answer(
                f"{chosen['name']}\nФото не найдено.\n{chosen['desc']}"
            )

        extra["current_product"] = chosen
        extra["current_product_list_id"] = extra.get("last_products_id")
        user_repo.update_extra_data(user, extra)
        await state.set_state(OrderStates.product_card)
    else:
        await message.answer(
            "Не удалось определить, какой товар вы выбрали. Пожалуйста, введите номер или точное название товара из последней выдачи."
        )


@router.message(StateFilter(OrderStates.waiting_for_choice), F.text)
async def handle_product_choice(message: Message, state: FSMContext):
    user_message = message.text or ""
    user = user_repo.get_or_create(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    )
    extra = json.loads(user.extra_data) if user.extra_data else {}

    last_products = extra.get("last_products", [])
    if not last_products:
        await message.answer(
            "Список товаров устарел. Пожалуйста, выполните новый поиск."
        )
        await state.clear()
        return

    chosen = None
    try:
        num = int(user_message)
        if 1 <= num <= len(last_products):
            chosen = last_products[num - 1]
    except ValueError:
        for prod in last_products:
            if (
                prod["name"].lower() in user_message.lower()
                or user_message.lower() in prod["name"].lower()
            ):
                chosen = prod
                break

    if chosen:
        file_path = Path.cwd() / chosen["image_url"]
        if file_path.exists():
            photo = FSInputFile(str(file_path))
            caption = f"{chosen['name']} — {chosen['price']}₽\n{chosen['desc']}"
            await message.answer_photo(
                photo,
                caption=caption
                + "\n\nХотите оформить заказ на этот товар? Напишите 'оформить заказ' или свяжитесь с менеджером.",
            )
        else:
            await message.answer(
                f"{chosen['name']}\nФото не найдено.\n{chosen['desc']}"
            )

        extra["current_product"] = chosen
        extra["current_product_list_id"] = extra.get("last_products_id")
        user_repo.update_extra_data(user, extra)
        await state.set_state(OrderStates.product_card)
    else:
        await message.answer(
            "Не удалось определить, какой товар вы выбрали. Пожалуйста, введите номер или точное название товара из последней выдачи."
        )


@router.message(StateFilter(OrderStates.product_card), F.text)
async def handle_product_card(message: Message, state: FSMContext):
    user_message = message.text or ""
    user = user_repo.get_or_create(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        message.from_user.last_name,
    )
    extra = json.loads(user.extra_data) if user.extra_data else {}
    current_product = extra.get("current_product")

    if not current_product:
        await message.answer(Messages.PRODUCT_NOT_FOUND)
        await state.clear()
        return

    user_message_lower = user_message.lower()

    if any(
        word in user_message_lower
        for word in ["фото", "картинка", "photo", "picture", "покажи", "show"]
    ):
        if current_product["image_url"].startswith("images/"):
            file_path = Path.cwd() / current_product["image_url"]
            if file_path.exists():
                photo = FSInputFile(str(file_path))
                await message.answer_photo(photo, caption=current_product["name"])
            else:
                await message.answer(
                    Messages.PHOTO_NOT_FOUND.format(name=current_product["name"])
                )
        else:
            await message.answer_photo(
                current_product["image_url"], caption=current_product["name"]
            )

    elif any(
        word in user_message_lower
        for word in [
            "характеристики",
            "характеристика",
            "описание",
            "подробности",
            "детали",
            "specs",
            "specifications",
        ]
    ):
        await message.answer(
            f"📋 Характеристики {current_product['name']}:\n\n{current_product['desc']}\n\n💰 Цена: {current_product['price']}₽"
        )

    elif any(
        word in user_message_lower
        for word in ["цена", "стоимость", "price", "cost", "сколько стоит"]
    ):
        await message.answer(
            f"💰 Цена {current_product['name']}: {current_product['price']}₽"
        )

    elif any(
        word in user_message_lower
        for word in [
            "заказ",
            "купить",
            "приобрести",
            "оформить",
            "order",
            "buy",
            "purchase",
        ]
    ):
        await message.answer(
            f"🛒 Оформление заказа на {current_product['name']}\n\n"
            f"Для оформления заказа свяжитесь с нашим менеджером:\n"
            f"📞 Телефон: +7 (800) 555-0123\n"
            f"📧 Email: order@technomarket.ru\n"
            f"💬 Telegram: @technomarket_support\n\n"
            f"Или оставьте свой номер телефона, и мы перезвоним вам в течение 15 минут."
        )
        await state.set_state(OrderStates.waiting_for_contact)

    elif any(
        word in user_message_lower
        for word in [
            "назад",
            "список",
            "другие",
            "еще",
            "back",
            "list",
            "other",
            "more",
        ]
    ):
        await message.answer(Messages.CHOOSE_ANOTHER)
        await state.clear()

    else:
        context = f"""Ты — консультант магазина "ТехноМаркет". Пользователь задает вопрос о товаре:

Товар: {current_product['name']}
Описание: {current_product['desc']}
Цена: {current_product['price']}₽

Вопрос пользователя: {user_message}

Отвечай кратко и по делу. Если пользователь спрашивает о характеристиках, которые не указаны в описании, вежливо сообщи, что эта информация временно недоступна и предложи связаться с менеджером для уточнения деталей."""

        reply = await get_gpt_response(user_message, context)
        if not reply or not reply.strip():
            await message.answer(Messages.NO_ANSWER)
        else:
            await message.answer(reply)
