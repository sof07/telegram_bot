from aiogram import Router, types, Bot

from aiogram.filters import CommandStart
from app.services.services import chat_members
from app.crud.group import crud_group
from sqlalchemy.ext.asyncio import AsyncSession


router = Router()


@router.message(CommandStart())
async def start(message: types.Message, bot: Bot, session: AsyncSession):
    chat: types.Chat = message.chat
    user_data: list[dict] = await chat_members(chat.id)
    # Записывает пользователей в базу данных связывая их с группой
    await crud_group.add_chat_members_to_db(
        chat=chat, user_data=user_data, session=session
    )
    print(user_data)
