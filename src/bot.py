import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import router
from openai_api import check_openai_account

LOG_BOT_STARTED = "[ТехноМаркет] Бот успешно запущен и готов к работе с клиентами."
LOG_CONTEXT_READY = "[ТехноМаркет] Контекст бизнес-ассистента подключён. Все обращения клиентов будут обработаны корректно."

async def main() -> None:
    """Точка входа для запуска Telegram-бота."""
    try:
        # await check_openai_account()
        logging.info(LOG_BOT_STARTED)
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher(storage=MemoryStorage())
        dp.include_router(router)
        logging.info(LOG_CONTEXT_READY)
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"[ТехноМаркет] Критическая ошибка запуска бота: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 