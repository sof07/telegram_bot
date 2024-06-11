from pyrogram import Client
from pyrogram.types import ChatMember
from aiogram import types, Bot

from app.core.config import settings


api_id = settings.api_id
api_hash = settings.api_hash
bot_token = settings.management_bot_token


# Функция проверки статуса пользователя (админ или создатель)
async def is_admin_or_creator(member: ChatMember) -> bool:
    # Проверить статус
    print('==============================')
    print(f'Проверка статуса админ или создатель {member.status in (
        'ChatMemberStatus.OWNER',
        'ChatMemberStatus.ADMINISTRATOR',
    )}')
    return member.status in (
        'ChatMemberStatus.OWNER',
        'ChatMemberStatus.ADMINISTRATOR',
    )


# Функция получения участников чата
async def chat_members(chat_id):
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
    user_list: list[dict, dict],
    check_user_list: list[int],
    bot: Bot,
    message: types.Message,
):
    diff_set = set(user_list.keys()).difference(set(check_user_list))
    list_user_name = []
    for id in diff_set:
        list_user_name.append(user_list[id]['user_name'])
    await bot.send_message(
        chat_id=message.from_user.id,
        text=f'Не отписавшиеся пользователи: {list_user_name}',
    )
