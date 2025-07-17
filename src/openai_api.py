import openai
import logging
import json
import os
from config import OPENAI_API_KEY, GROQ_API_KEY
from context import context_manager
from typing import Optional

OPENAI_ENDPOINT = "https://api.openai.com/v1"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1"
DEFAULT_MODEL_OPENAI = "gpt-3.5-turbo"
DEFAULT_MODEL_GROQ = "llama3-70b-8192"
ERROR_MSG = "Извините, не удалось получить ответ от ассистента."
PROVIDERS = {
    "OpenAI": {"api_key": OPENAI_API_KEY, "endpoint": OPENAI_ENDPOINT, "default_model": DEFAULT_MODEL_OPENAI},
    "Groq": {"api_key": GROQ_API_KEY, "endpoint": GROQ_ENDPOINT, "default_model": DEFAULT_MODEL_GROQ},
}

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    openai.api_base = "https://api.openai.com/v1"
    _current_provider = "OpenAI"
elif GROQ_API_KEY:
    openai.api_key = GROQ_API_KEY
    openai.api_base = "https://api.groq.com/openai/v1"
    _current_provider = "Groq"
else:
    raise RuntimeError("Не найден ни один API-ключ: ни OPENAI_API_KEY, ни GROQ_API_KEY")

logging.basicConfig(level=logging.ERROR)
logging.warning(f"[AI Provider] Выбран: {_current_provider}, endpoint: {openai.api_base}")

async def check_openai_account() -> None:
    """Проверяет доступность аккаунта OpenAI/Groq и выводит информацию в лог."""
    try:
        models = await openai.Model.alist()
        logging.info(f"[{_current_provider}] API-ключ начинается с: {str(openai.api_key)[:8]}... (скрыто)")
        logging.info(f"[{_current_provider}] Тип ответа models: {type(models)}; Пример содержимого: {str(models)[:200]}")
    except Exception as e:
        logging.error(f"[{_current_provider}] Ошибка проверки аккаунта: {e}")

async def get_gpt_response(user_message: str, context: str = "", model: Optional[str] = None) -> str:
    """Получить ответ от LLM (OpenAI/Groq) с учётом контекста и выбранной модели."""
    if not context:
        context = context_manager.get_context()
    if not model:
        model = PROVIDERS[_current_provider]["default_model"]
    try:
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_message}
            ]
        )
        if isinstance(response, str):
            response = json.loads(response)
        return response['choices'][0]['message']['content']  # type: ignore
    except Exception as e:
        logging.error(f"{_current_provider} API error: {e}")
        return ERROR_MSG

async def get_category_by_llm(user_message: str) -> str:
    """Определяет категорию товара из запроса пользователя через LLM."""
    prompt = (
        f"Пользователь написал: '{user_message}'. "
        "Определи, к какой из этих категорий относится его запрос: "
        "Смартфоны, Планшеты, Ноутбуки, Телевизоры, Наушники, Смарт-часы, Фотоаппараты, Игровые приставки, Мониторы, Аксессуары. "
        "Ответь только одним словом — названием категории из списка. Если не удалось определить, напиши 'Неизвестно'."
    )
    try:
        response = await get_gpt_response(user_message, prompt)
        category = response.strip().split()[0]
        return category.capitalize()
    except Exception:
        return "Неизвестно" 