from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeDefault,
    BotCommandScopeAllGroupChats,
)

MENU_BUTTONS_TEXT: dict[str, str] = {
    '/start': 'Запуск бота, доступна только админам',
    '/help': 'Справка по работе бота',
}


async def main_menu(bot: Bot):
    # Команды для приватных чатов
    main_menu_commands = [
        BotCommand(command=command, description=description)
        for command, description in MENU_BUTTONS_TEXT.items()
    ]
    # удаление команд бота для чатов, команды видны только в меню бота
    await bot.delete_my_commands(scope=BotCommandScopeDefault())
    await bot.delete_my_commands(scope=BotCommandScopeAllGroupChats())
    await bot.set_my_commands(main_menu_commands, BotCommandScopeAllPrivateChats())
