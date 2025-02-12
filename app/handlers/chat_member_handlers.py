from aiogram import F, Router, types
from aiogram.filters.chat_member_updated import (IS_ADMIN, IS_NOT_MEMBER,
                                                 JOIN_TRANSITION, KICKED,
                                                 LEAVE_TRANSITION, LEFT,
                                                 MEMBER, PROMOTED_TRANSITION,
                                                 RESTRICTED,
                                                 ChatMemberUpdatedFilter)
from aiogram.types import ChatMemberUpdated
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_group, crud_user_group_association, user_crud
from app.models import UserGroupAssociation
from app.services.services import chat_members

router = Router()
router.my_chat_member.filter(F.chat.type.in_({'group', 'supergroup'}))


async def update_admin_status(
    event: ChatMemberUpdated, session: AsyncSession, status: bool
) -> None:
    """
    Универсальная функция обновления статуса администратора пользователя.

    :param event: Объект обновления статуса чата.
    :param session: Асинхронная сессия для работы с базой данных.
    :param status: Новый статус администратора (True - назначен, False - снят).
    """
    chat_id: types.Chat = event.chat.id
    user_id: int = event.new_chat_member.user.id
    await crud_user_group_association.update_admin_status(
        group_id=chat_id,
        user_id=user_id,
        admin_status=status,
        session=session,
    )


# my_chat_member отлавливает события связанные с ботом
@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=PROMOTED_TRANSITION)
)
async def add_group_to_database(
    event: ChatMemberUpdated, session: AsyncSession
) -> None:
    """
    Добавляет группу и ее участников в базу данных после повышения бота в админы.

    :param event: Объект обновления статуса чата.
    :param session: Асинхронная сессия для работы с базой данных.
    """

    chat: types.Chat = event.chat  # Объект чата из которого отправлена команда start
    # Функция возвращает список пользователей из чата
    user_data = await chat_members(chat.id)
    # Записывает пользователей в базу данных связывая их с группой
    await crud_group.add_chat_members_to_db(
        chat=chat, user_data=user_data, session=session
    )


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER))
async def kicked_bot_from_group(
    event: ChatMemberUpdated,
    session: AsyncSession,
) -> None:
    """
    Удаляет группу из базы данных после исключения бота.

    :param event: Объект обновления статуса чата.
    :param session: Асинхронная сессия для работы с базой данных.
    """
    chat: types.Chat = event.chat  # Объект чата из которого отправлена команда start
    # Функция возвращает список пользователей из чата
    group_data = await crud_group.get_group(
        group_id=chat.id,
        session=session,
    )
    # Записывает пользователей в базу данных связывая их с группой
    await crud_group.remove(
        db_obj=group_data,
        session=session,
    )


# chat_member отлавливает события связанные с пользователями
@router.chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=(KICKED | LEFT | RESTRICTED | MEMBER) >> IS_ADMIN
    )
)
async def admin_true(event: ChatMemberUpdated, session: AsyncSession) -> None:
    """
    Обновляет статус пользователя, если он стал администратором в группе.

    :param event: Объект обновления статуса чата.
    :param session: Асинхронная сессия для работы с базой данных.
    """
    await update_admin_status(event, session, True)


@router.chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=(KICKED | LEFT | RESTRICTED | MEMBER) << IS_ADMIN
    )
)
async def admin_false(event: ChatMemberUpdated, session: AsyncSession) -> None:
    """
    Обновляет статус пользователя, если он больше не является администратором.

    :param event: Объект обновления статуса чата.
    :param session: Асинхронная сессия для работы с базой данных.
    """
    await update_admin_status(event, session, False)


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def user_leave(event: ChatMemberUpdated, session: AsyncSession) -> None:
    """
    Обрабатывает выход пользователя из группы и обновляет базу данных.

    :param event: Объект обновления статуса чата.
    :param session: Асинхронная сессия для работы с базой данных.
    """
    chat_id: types.Chat = event.chat.id
    user_id: int = event.new_chat_member.user.id
    user_group_association: UserGroupAssociation = (
        await crud_user_group_association.get_user_from_chat(
            group_id=chat_id,
            user_id=user_id,
            session=session,
        )
    )
    if user_group_association:
        await crud_user_group_association.remove(
            db_obj=user_group_association,
            session=session,
        )
    chats_where_user = await crud_user_group_association.get_chat_where_user_id(
        user_id=user_id, session=session
    )
    if not chats_where_user:
        user = await user_crud.get_user(user_id=user_id, session=session)
        await user_crud.remove(db_obj=user, session=session)


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def user_join(event: ChatMemberUpdated, session: AsyncSession) -> None:
    """
    Добавляет нового пользователя в базу данных после его вступления в группу.

    :param event: Объект обновления статуса чата.
    :param session: Асинхронная сессия для работы с базой данных.
    """
    chat: types.Chat = event.chat
    user_id: int = event.new_chat_member.user.id
    user_name: str = event.new_chat_member.user.username
    user_first_name: str = event.new_chat_member.user.first_name
    user_last_name: str = event.new_chat_member.user.last_name
    user: list[dict[str, str]] = [
        {
            'user_id': user_id,
            'user_name': user_name,
            'first_name': user_first_name,
            'last_name': user_last_name,
            'is_admin_or_creator': False,
        }
    ]
    await crud_group.add_chat_members_to_db(chat=chat, user_data=user, session=session)
