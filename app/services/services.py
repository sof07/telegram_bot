import random
import string

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.markdown import bold
from pyrogram import Client, utils
from pyrogram.types import ChatMember

from app.core.config import settings

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


# Экранирует символы в тексте
def escape_markdown(text: str) -> str:
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)


async def send_message_to_admin(
    admin_list: list[int],
    user_list: list[str],
    bot: Bot,
) -> None:
    text_if_user_list: str = bold(escape_markdown('Возможно эти ребята косячат:'))
    text_if_not_user_list: str = bold(escape_markdown('Сегодня все молодцы!'))

    if admin_list:
        for admin_id in admin_list:
            if user_list:
                escaped_user_list = [escape_markdown(user) for user in user_list]
                await bot.send_message(
                    chat_id=admin_id,
                    text=f'{text_if_user_list} \n👉 {"\n👉 ".join(escaped_user_list)}',
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
            else:
                await bot.send_message(
                    chat_id=admin_id,
                    text=text_if_not_user_list,
                    parse_mode=ParseMode.MARKDOWN_V2,
                )


def random_alphanumeric_string(length):
    """Генератор пароля"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_birthday_message(name):
    messages = [
        bold(
            f'Сегодня @{name} празднует день рождения! Поздравляю! Желаю крепкого здоровья, огромного счастья, успехов в делах и исполнения всех желаний. Пусть каждый день приносит радость, а рядом будут верные друзья и близкие! 🎉🎂✨',
        ),
        bold(
            f'Сегодня @{name} празднует день рождения! Пусть в жизни будет больше ярких моментов, радостных событий и добрых людей. Желаю здоровья, финансового благополучия и нескончаемой энергии для новых свершений! 🎈🎁'
        ),
        bold(
            f'Сегодня @{name} празднует день рождения! Поздравляю! Пусть удача сопровождает тебя во всех начинаниях, мечты становятся реальностью, а в доме всегда царят тепло, уют и достаток. Счастья и долгих лет жизни! 🎂✨'
        ),
        bold(
            f'Сегодня @{name} празднует день рождения! Желаю огромного запаса здоровья, чтобы сил хватало на все желания и мечты! Пусть каждый день приносит радость, а рядом будут надежные друзья и любящие близкие! 🎉🥳'
        ),
        bold(
            f'Сегодня @{name} празднует день рождения! Поздравляю! Пусть каждый новый день будет полон возможностей, радости и вдохновения. Желаю крепкого здоровья, большого счастья и уверенности в завтрашнем дне! 🎂🎈'
        ),
        bold(
            f'Сегодня @{name} празднует день рождения! От всей души желаю счастья, благополучия и тепла! Пусть работа приносит удовольствие, отдых заряжает энергией, а жизнь радует приятными сюрпризами! 🎉🎁'
        ),
        bold(
            f'Сегодня @{name} празднует день рождения! Пусть этот день будет полон радости, улыбок и самых теплых пожеланий. Желаю здоровья, удачи, успехов во всех делах и исполнения самых заветных желаний! 🥳🎂'
        ),
        bold(
            f'Сегодня @{name} празднует день рождения! Поздравляю! Желаю, чтобы каждый день приносил только положительные эмоции, близкие окружали заботой, а мечты сбывались легко и быстро! 🎈🎉'
        ),
        bold(
            f'Сегодня @{name} празднует день рождения! Желаю крепкого здоровья, финансового достатка, ярких впечатлений и много счастливых моментов. Пусть жизнь будет наполнена только хорошими событиями! 🎂🎁'
        ),
        bold(
            f'Сегодня @{name} празднует день рождения! Поздравляю! Пусть в жизни будет больше приятных встреч, неожиданных радостей и больших побед. Счастья, здоровья и удачи во всех начинаниях! 🎉✨'
        ),
    ]
    return random.choice(messages)
