from pyrogram import Client
from pyrogram.types import ChatMember
from aiogram import Bot
from pyrogram import utils
from app.core.config import settings
from aiogram.utils import markdown
from aiogram.enums import ParseMode


api_id = settings.api_id
api_hash = settings.api_hash
bot_token = settings.management_bot_token


# Исправляет ошибку в библиотеке pyrogram которая
# вызывает исключение Peer id invalid:
def get_peer_type_new(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith('-'):
        return 'user'
    elif peer_id_str.startswith('-100'):
        return 'channel'
    else:
        return 'chat'


utils.get_peer_type = get_peer_type_new


# Функция проверки статуса пользователя (админ или создатель)
async def is_admin_or_creator(member: ChatMember) -> bool:
    """Получает статус пользователя и проверяет его на админа или создателя."""

    return str(member.status.name) in (
        'OWNER',
        'ADMINISTRATOR',
    )


# Функция получения участников чата
async def chat_members(chat_id: int) -> list[dict]:
    """Получает список участников чата."""

    user_data: list[dict] = []
    app = Client(
        'Имя_Бот',
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token,
        in_memory=True,
    )
    await app.start()
    async for member in app.get_chat_members(chat_id):
        if not member.user.is_bot:  # если пользователь не бот
            user_data.append(
                {
                    'user_id': member.user.id,
                    'first_name': member.user.first_name,
                    'last_name': member.user.last_name,
                    'user_name': member.user.username,
                    'is_admin_or_creator': await is_admin_or_creator(member),
                }
            )
    await app.stop()
    return user_data


async def send_message_to_admin(
    admin_list: list[int],
    user_list: list[str],
    bot: Bot,
) -> None:
    text_if_user_list: str = markdown.bold('Список засранцев:')
    text_if_not_user_list: str = markdown.bold('Сегодня все молодцы!')
    if admin_list:
        for admin_id in admin_list:
            if user_list:
                await bot.send_message(
                    chat_id=admin_id,
                    text=f'{text_if_user_list} \n👉 {'\n👉 '.join(user_list)}',
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
            else:
                await bot.send_message(
                    chat_id=admin_id, text=f'{text_if_not_user_list}'
                )
