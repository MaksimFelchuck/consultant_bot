from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import SessionLocal
from database.models import User, Product, Category, Message as DBMessage
from openai_api import get_gpt_response
import logging
import re
from database.service import get_or_create_user, save_message, get_random_products_for_category
from sqlalchemy.orm import Session

# Define the keys for preferences
PREFERENCE_KEYS = ["category", "brand", "budget", "color", "characteristics"]

router = Router()

class OrderStates(StatesGroup):
    waiting_for_choice = State()
    product_card = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Добро пожаловать в ТехноМаркет! 🛒\n\n"
        "Я — виртуальный помощник компании 🤖. Готов помочь с выбором техники, консультацией по товарам и оформлением заказа!\n\n"
        "В нашем магазине есть такие категории:\n"
        "• Смартфоны\n• Планшеты\n• Ноутбуки\n• Телевизоры\n• Наушники\n• Смарт-часы\n• Фотоаппараты\n• Игровые приставки\n• Мониторы\n• Аксессуары\n\n"
        "Что вас интересует? Пишите прямо сюда! 😊\n\n"
        "📦 Доставка по РФ | 💳 Оплата онлайн/наличными | 🛡 Гарантия 1 год\n\n"
        "Сайт: https://technomarket.ru\n\n"
        "⚠️ Внимание: бот тестовый, фото товаров не настоящие, заказы не обрабатываются."
    )

@router.message(F.text)
async def handle_message(message: Message, state: FSMContext):
    session = SessionLocal()
    try:
        telegram_id = str(message.from_user.id)
        username = message.from_user.username or ""
        user = get_or_create_user(session, telegram_id, username=username)
        if not user or not hasattr(user, "id"):
            await message.answer("Ошибка идентификации пользователя. Попробуйте позже.")
            return
        save_message(session, user.id, "user", message.text or "")
        data = await state.get_data()
        preferences = data.get("preferences", {})
        history = data.get("history", [])
        product_list_ids = data.get("product_list", [])
        selected_product_id = data.get("selected_product_id")
        dialog = history[-3:] + [message.text or ""]
        llm_input = "\n".join(dialog)
        from context import context_manager
        context = context_manager.get_context()
        llm_response = await get_gpt_response(llm_input, context)
        extracted = {}
        import re
        match = re.search(r"Параметры поиска:([^\n]*)", llm_response)
        if match:
            params = match.group(1)
            for key in PREFERENCE_KEYS:
                m = re.search(fr"{key}\s*=\s*([^,]*)", params)
                if m:
                    extracted[key] = m.group(1).strip()
        preferences.update({k: v for k, v in extracted.items() if v})
        history.append(message.text or "")
        await state.update_data(preferences=preferences, history=history)
        missing = [k for k in ["category", "budget", "brand", "color", "characteristics"] if not preferences.get(k)]
        if missing:
            questions = {
                "category": "какая категория техники вас интересует?",
                "budget": "какой у вас бюджет?",
                "brand": "предпочтительный бренд?",
                "color": "какой цвет предпочитаете?",
                "characteristics": "есть ли важные характеристики (например, размер экрана, камера)?"
            }
            ask = " ".join([questions[m] for m in missing])
            await message.answer(f"Спасибо! Уточните, пожалуйста: {ask}")
            return
        # --- Проверка: выбор товара по номеру или названию ---
        if product_list_ids and message.text:
            # Получаем список товаров из FSM
            products = session.query(Product).filter(Product.id.in_(product_list_ids)).all()
            # Проверяем, есть ли в сообщении номер или название товара
            chosen_product = None
            # 1. Поиск по номеру
            if message.text and message.text.strip().isdigit():
                idx = int(message.text.strip()) - 1
                if 0 <= idx < len(products):
                    chosen_product = products[idx]
            # 2. Поиск по названию (простое вхождение)
            if not chosen_product and message.text:
                for p in products:
                    pname = str(p.name) if p.name else ""
                    if pname.lower() in message.text.lower():
                        chosen_product = p
                        break
            if chosen_product:
                # Сохраняем выбранный товар в FSM
                await state.update_data(selected_product_id=getattr(chosen_product, 'id', None))
                # Показываем карточку товара
                pname = str(getattr(chosen_product, 'name', ''))
                pdesc = str(getattr(chosen_product, 'description', ''))
                pprice = str(getattr(chosen_product, 'price', ''))
                text = f"<b>{pname}</b>\n\n{pdesc}\n\nЦена: {pprice} ₽"
                # Отправляем фото, если есть
                image_url = getattr(chosen_product, 'image_url', None)
                image_url = str(image_url) if image_url and not isinstance(image_url, type(Product.image_url)) else None
                if image_url and image_url.strip():
                    try:
                        await message.answer_photo(image_url, caption=text, parse_mode="HTML")
                    except Exception:
                        await message.answer(text, parse_mode="HTML")
                else:
                    await message.answer(text, parse_mode="HTML")
                await message.answer("Если хотите узнать подробнее или заказать — напишите 'подробнее' или 'заказать'. Чтобы вернуться к списку — напишите 'назад'.")
                return
        # --- Обработка команд для выбранного товара ---
        if selected_product_id:
            selected_product = session.query(Product).filter(Product.id == selected_product_id).first()
            if selected_product:
                user_text = (message.text or '').strip().lower()
                if 'подробнее' in user_text:
                    # Показываем расширенную информацию
                    pname = str(getattr(selected_product, 'name', ''))
                    pdesc = str(getattr(selected_product, 'description', ''))
                    pprice = str(getattr(selected_product, 'price', ''))
                    specs = getattr(selected_product, 'specs', {})
                    specs_str = ''
                    if specs and isinstance(specs, dict):
                        specs_str = '\n'.join([f"{k}: {v}" for k, v in specs.items()])
                    text = f"<b>{pname}</b>\n\n{pdesc}\n\n{specs_str}\n\nЦена: {pprice} ₽"
                    await message.answer(text, parse_mode="HTML")
                    await message.answer("Чтобы заказать этот товар — напишите 'заказать'. Чтобы вернуться к списку — напишите 'назад'.")
                    return
                elif 'заказать' in user_text:
                    pname = str(getattr(selected_product, 'name', ''))
                    await message.answer(f"Ваш заказ на '{pname}' оформлен! (Тестовый режим, заказ не будет обработан)\n\nСпасибо за обращение в ТехноМаркет! Если хотите выбрать другой товар — напишите 'назад' или начните новый поиск.")
                    # Сбросить выбранный товар, оставить историю и фильтры
                    await state.update_data(selected_product_id=None)
                    return
                elif 'назад' in user_text:
                    # Вернуться к списку товаров
                    product_list_ids = data.get("product_list", [])
                    if product_list_ids:
                        products = session.query(Product).filter(Product.id.in_(product_list_ids)).all()
                        response = ["Вот что могу предложить:"]
                        for idx, p in enumerate(products, 1):
                            response.append(f"{idx}. {p.name}\n{p.description[:60]}...\nЦена: {p.price} ₽")
                        response.append("\nЕсли что-то заинтересовало — напишите номер или название товара, чтобы увидеть фото и подробности.")
                        await message.answer("\n\n".join(response))
                        await state.update_data(selected_product_id=None)
                        return
                    else:
                        await message.answer("Список товаров не найден. Начните новый поиск или уточните параметры.")
                        await state.update_data(selected_product_id=None)
                        return
        # --- Новый блок: подбор и показ товаров ---
        products_query = session.query(Product)
        if preferences.get("category"):
            category = session.query(Category).filter(Category.name.ilike(f"%{preferences['category']}%")) .first()
            if category:
                products_query = products_query.filter(Product.category_id == category.id)
        if preferences.get("brand"):
            products_query = products_query.filter(Product.name.ilike(f"%{preferences['brand']}%"))
        if preferences.get("budget"):
            try:
                price = int(re.sub(r"[^0-9]", "", preferences["budget"]))
                products_query = products_query.filter(Product.price <= price)
            except Exception:
                pass
        if preferences.get("color"):
            color = preferences["color"].lower()
            products_query = products_query.filter(Product.description.ilike(f"%{color}%"))
        if preferences.get("characteristics"):
            char = preferences["characteristics"].lower()
            products_query = products_query.filter(Product.description.ilike(f"%{char}%"))
        products = products_query.limit(5).all()
        if not products:
            await message.answer("К сожалению, по вашим параметрам ничего не найдено. Могу предложить рассмотреть другие варианты или изменить фильтры (например, увеличить бюджет, выбрать другой бренд или цвет). Напишите, что для вас важно — и я подберу что-то подходящее!")
            return
        response = ["Вот что могу предложить:"]
        for idx, p in enumerate(products, 1):
            response.append(f"{idx}. {p.name}\n{p.description[:60]}...\nЦена: {p.price} ₽")
        response.append("\nЕсли что-то заинтересовало — напишите номер или название товара, чтобы увидеть фото и подробности.")
        await message.answer("\n\n".join(response))
        await state.update_data(product_list=[p.id for p in products])
    except Exception as e:
        logging.error(f"[handle_message] Ошибка: {e}")
        await message.answer("Извините, произошла ошибка. Попробуйте ещё раз.")
    finally:
        session.close() 