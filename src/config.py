import os

BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_telegram_bot_token_here')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
DEFAULT_CONTEXT = """Ты — профессиональный помощник, который отвечает на вопросы клиентов от имени компании, магазина или эксперта. Отвечай вежливо, понятно и по делу.""" 

ENV = os.getenv("ENV", "DEV").upper()  # Всегда в верхнем регистре

if ENV == "DEV":
    # Подключение к dev-базе из docker-compose
    DATABASE_URL = "postgresql://postgres:postgres@db:5432/consultant_db"
elif ENV == "PROD":
    # Railway или другое prod-окружение
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    raise ValueError(f"Неизвестное окружение ENV={ENV}. Используйте 'DEV' или 'PROD'.") 