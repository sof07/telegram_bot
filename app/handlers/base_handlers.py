from aiogram import Router, types, F, Bot

from aiogram.filters import CommandStart

# from app.sheduler.sheduler import scheduler
from app.services.services import chat_members, send_message_to_admin
from app.crud.group import crud_group
from sqlalchemy.ext.asyncio import AsyncSession

# from app.keyboards.inline_keyboard import kb_analytics

router = Router()
user_list: dict[dict] = {}
check_user_list: list[int] = []  # Список пользователей которые отписались


@router.message(CommandStart())
async def start(message: types.Message, session: AsyncSession):
    chat: types.Chat = message.chat  # Объект чата из которого отправлена команда start
    user_data = await chat_members(
        chat.id
    )  # Функция возвращает список пользователей из чата
    await crud_group.add_chat_members_to_db(
        chat=chat, user_data=user_data, session=session
    )  # Записывает пользователей в базу данных связывая их с группой

    # await message.reply('Участники чата успешно сохранены в базу данных.')


@router.message(F.text.contains('Порядок') | F.text.contains('порядок'))
async def message_photo_caption_please(message: types.Message, bot: Bot):
    check_user_list.append(message.from_user.id)
    await bot.send_message(
        chat_id=message.from_user.id,
        text=f'Пользователь {message.from_user.username} +',
    )
    print(check_user_list)


# Админы:
# пользователи со статусом одмин могут получать сообщения со списком не отписавшихся
# админы могут отписатьсяся от получения сообщений
# админ может подписать админа на получения сообщений

# проблема получения айди чата во время выполнения шедулера
