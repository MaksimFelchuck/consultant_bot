import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import router


async def main():
    # await check_openai_account()
    logging.info("[ТехноМаркет] Бот успешно запущен и готов к работе с клиентами.")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    logging.info(
        "[ТехноМаркет] Контекст бизнес-ассистента подключён. Все обращения клиентов будут обработаны корректно."
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
