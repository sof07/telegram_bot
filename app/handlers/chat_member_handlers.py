from aiogram import F, Router, types
from aiogram.filters.chat_member_updated import (IS_ADMIN, JOIN_TRANSITION,
                                                 KICKED, LEAVE_TRANSITION,
                                                 LEFT, MEMBER,
                                                 PROMOTED_TRANSITION,
                                                 RESTRICTED,
                                                 ChatMemberUpdatedFilter)
from aiogram.types import ChatMemberUpdated
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_user_group_association
from app.crud.group import crud_group
from app.services.services import chat_members

router = Router()
router.my_chat_member.filter(F.chat.type.in_({'group', 'supergroup'}))


# my_chat_member отлавливает события связанные с ботом
@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=PROMOTED_TRANSITION)
)
async def add_group_to_database(
    event: ChatMemberUpdated, session: AsyncSession
) -> None:
    """
    Обрабатывает событие повышения статуса бота до администратора и добавляет группу в базу данных.

    :param event: Объект события обновления участника чата.
    :param session: Асинхронная сессия SQLAlchemy.
    """
    chat: types.Chat = event.chat  # Объект чата из которого отправлена команда start
    # Функция возвращает список пользователей из чата
    user_data = await chat_members(chat.id)
    # Записывает пользователей в базу данных связывая их с группой
    await crud_group.add_chat_members_to_db(
        chat=chat, user_data=user_data, session=session
    )


# chat_member отлавливает события связанные с пользователями
@router.chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=(KICKED | LEFT | RESTRICTED | MEMBER) >> IS_ADMIN
    )
)
async def admin_true(event: ChatMemberUpdated, session: AsyncSession) -> None:
    """
    Обрабатывает событие повышения пользователя до администратора.

    :param event: Объект события обновления участника чата.
    :param session: Асинхронная сессия SQLAlchemy.
    """
    chat_id: types.Chat = event.chat.id
    user_id: int = event.new_chat_member.user.id
    await crud_user_group_association.update_admin_status(
        group_id=chat_id,
        user_id=user_id,
        admin_status=True,
        session=session,
    )


@router.chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=(KICKED | LEFT | RESTRICTED | MEMBER) << IS_ADMIN
    )
)
async def admin_false(event: ChatMemberUpdated, session: AsyncSession) -> None:
    """
    Обрабатывает событие понижения пользователя с администратора.

    :param event: Объект события обновления участника чата.
    :param session: Асинхронная сессия SQLAlchemy.
    """
    chat_id: types.Chat = event.chat.id
    user_id: int = event.new_chat_member.user.id
    await crud_user_group_association.update_admin_status(
        group_id=chat_id,
        user_id=user_id,
        admin_status=False,
        session=session,
    )


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def user_leave(event: ChatMemberUpdated, session: AsyncSession) -> None:
    chat_id: types.Chat = event.chat.id
    user_id: int = event.new_chat_member.user.id
    # CRUD Удалить запись о пользователе из БД
    pass


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def user_join(event: ChatMemberUpdated, session: AsyncSession) -> None:
    chat_id: types.Chat = event.chat.id
    user_id: int = event.new_chat_member.user.id
    # CRUD Добавить запись о пользователе из БД
    pass
