import os

BOT_TOKEN = os.getenv('BOT_TOKEN', 'your_telegram_bot_token_here')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
DEFAULT_CONTEXT = """Ты — профессиональный помощник, который отвечает на вопросы клиентов от имени компании, магазина или эксперта. Отвечай вежливо, понятно и по делу.""" 