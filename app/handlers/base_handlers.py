from aiogram import Router, types, F, Bot

from aiogram.filters import CommandStart

from app.services.services import chat_members
from app.crud.group import crud_group
from app.crud.user_group_association import crud_user_group_association
from sqlalchemy.ext.asyncio import AsyncSession


router = Router()


@router.message(CommandStart())
async def start(message: types.Message, bot: Bot, session: AsyncSession):
    chat: types.Chat = message.chat  # Объект чата из которого отправлена команда start
    # Функция возвращает список пользователей из чата
    user_data = await chat_members(chat.id)
    # Записывает пользователей в базу данных связывая их с группой
    await crud_group.add_chat_members_to_db(
        chat=chat, user_data=user_data, session=session
    )


@router.message(F.text.contains('Порядок') | F.text.contains('порядок'))
async def message_photo_caption_please(
    message: types.Message, session: AsyncSession
) -> None:
    group_id: int = message.chat.id
    user_id: int = message.from_user.id
    session = session
    await crud_user_group_association.update_status_can_receive_messages_true(
        group_id,
        user_id,
        session,
    )
