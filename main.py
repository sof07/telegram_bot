import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.core.config import settings

from app.core.db import AsyncSessionLocal


from app.handlers import base_handlers
from app.keyboards.set_menu import main_menu

from app.middlewares.middleware import DataBaseSession
from app.logs.logger import configure_logging
from app.sheduler.sheduler import scheduler
# Кнопки меню


async def main():
    configure_logging('management_bot')
    logging.info('Запуск бота - management_bot.')
    bot = Bot(token=settings.management_bot_token)
    dp = Dispatcher(bot=bot)
    scheduler.start()
    dp.update.middleware(DataBaseSession(async_session=AsyncSessionLocal))
    dp.include_router(base_handlers.router)
    # dp.include_router(handlers.router)

    dp.startup.register(main_menu)
    # await create_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error('Ошибка запуска бота')
