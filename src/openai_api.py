import json
import logging
import os

import openai

from src.config import GROQ_API_KEY, OPENAI_API_KEY
from src.context import context_manager

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
logging.warning(
    f"[AI Provider] Выбран: {_current_provider}, endpoint: {openai.api_base}"
)


async def check_openai_account():
    try:
        models = await openai.Model.alist()
        logging.info(
            f"[{_current_provider}] API-ключ начинается с: {str(openai.api_key)[:8]}... (скрыто)"
        )
        logging.info(
            f"[{_current_provider}] Тип ответа models: {type(models)}; Пример содержимого: {str(models)[:200]}"
        )
    except Exception as e:
        logging.error(f"[{_current_provider}] Ошибка проверки аккаунта: {e}")


async def get_gpt_response(
    user_message: str, context: str = "", model: str | None = None
):
    if not context:
        context = context_manager.get_context()
    # Выбор модели по провайдеру
    if not model:
        if _current_provider == "OpenAI":
            model = "gpt-3.5-turbo"
        elif _current_provider == "Groq":
            model = "llama3-70b-8192"
        else:
            model = "gpt-3.5-turbo"  # fallback
    try:
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_message},
            ],
        )
        # Универсальное приведение к dict
        if isinstance(response, str):
            response = json.loads(response)
        return response["choices"][0]["message"]["content"]  # type: ignore
    except Exception as e:
        logging.error(f"{_current_provider} API error: {e}")
        return "Извините, не удалось получить ответ от ассистента."
