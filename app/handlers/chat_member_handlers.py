from aiogram import Router, types, F
from aiogram.filters.chat_member_updated import (
    PROMOTED_TRANSITION,
    ChatMemberUpdatedFilter,
)
from aiogram.types import ChatMemberUpdated
from app.services.services import chat_members
from app.crud.group import crud_group

from sqlalchemy.ext.asyncio import AsyncSession


router = Router()
router.my_chat_member.filter(F.chat.type.in_({'group', 'supergroup'}))


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=PROMOTED_TRANSITION)
)
async def add_group_to_database(
    event: ChatMemberUpdated, session: AsyncSession
) -> None:
    chat: types.Chat = event.chat  # Объект чата из которого отправлена команда start
    print(f'>>>>>>>{chat.id}')
    # Функция возвращает список пользователей из чата
    user_data = await chat_members(chat.id)
    # Записывает пользователей в базу данных связывая их с группой
    await crud_group.add_chat_members_to_db(
        chat=chat, user_data=user_data, session=session
    )
