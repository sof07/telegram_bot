from aiogram import Bot
from aiogram.types import BotCommand

MENU_BUTTONS_TEXT: dict[str, str] = {
    '/start': 'Запуск бота, доступна только админам',
    '/help': 'Справка по работе бота',
}


async def main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command=command, description=description)
        for command, description in MENU_BUTTONS_TEXT.items()
    ]
    await bot.set_my_commands(main_menu_commands)
