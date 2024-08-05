from aiogram import types
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.group import Group
from app.models.user import User
from app.models.user_group_association import UserGroupAssociation


class CRUDUserGroupAssociation(CRUDBase):
    """CRUD для модели UserGroupAssociation."""

    async def get_user_from_chat(
        self,
        group_id: int,
        user_id: int,
        session: AsyncSession,
    ) -> UserGroupAssociation | None:
        """
        Получает связку пользователь -> чат.

        Аргументы:
            group_id - id чата
            user_id - id пользователя
        Возвращает:
            user_group_association: UserGroupAssociation | None
            Тело запроса:
              - выбрать из таблицы UserGroupAssociation все записи
              - где поле user_id равно Id пользователя
              - и поле group_id равно Id группы
        """
        user_group_association: UserGroupAssociation | None = await session.execute(
            select(self.model).where(
                and_(
                    self.model.user_id == user_id,
                    self.model.group_id == group_id,
                )
            )
        )
        return user_group_association.scalars().first()

    async def get_user_canrecive_message_status(
        self,
        group_id: int,
        can_receive_messages_status: bool,
        rceive_newsletter_status: bool,
        not_included_in_report_status: bool,
        is_admin: bool,
        session: AsyncSession,
    ) -> list[UserGroupAssociation]:
        """ "
        Получает ID чата, возвращает список объектов UserGroupAssociation
        с статусом can_recive_message False
        """
        user_canrecive_message: UserGroupAssociation | None = await session.execute(
            select(self.model)
            .options(
                selectinload(self.model.user)
            )  # для получения связаных данных из модели user
            .where(
                and_(
                    self.model.group_id == group_id,
                    self.model.can_receive_messages == can_receive_messages_status,
                    self.model.rceive_newsletter == rceive_newsletter_status,
                    self.model.not_included_in_report == not_included_in_report_status,
                    self.model.is_admin == is_admin,
                )
            )
        )
        return user_canrecive_message.scalars().all()

    async def get_user_crceive_newsletter_status(
        self,
        group_id: int,
        rceive_newsletter_status: bool,
        session: AsyncSession,
    ) -> list[UserGroupAssociation]:
        """ "
        Получает ID чата, возвращает список объектов UserGroupAssociation
        с статусом rceive_newsletter False или True
        """
        user_canrecive_message: UserGroupAssociation | None = await session.execute(
            select(self.model)
            .options(
                selectinload(self.model.user)
            )  # для получения связаных данных из модели user
            .where(
                and_(
                    self.model.group_id == group_id,
                    self.model.rceive_newsletter == rceive_newsletter_status,
                )
            )
        )
        return user_canrecive_message.scalars().all()

    async def update_all_can_receive_messages_false(self, session: AsyncSession):
        """Устанавливает в поле can_receive_messages всех пользователей в False."""
        await session.execute(update(self.model).values(can_receive_messages=False))
        await session.commit()

    async def update_status_can_receive_messages_true(
        self,
        group_id: int,
        user_id: int,
        session: AsyncSession,
    ) -> None:
        """
        Устанавливает в поле can_receive_messages пользователя в True.
        Аргументы:
            group_id - id чата
            user_id - id пользователя
        """
        await session.execute(
            update(self.model)
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.group_id == group_id,
                )
            )
            .values(can_receive_messages=True)
        )
        await session.commit()

    async def update_admin_status(
        self,
        group_id: int,
        user_id: int,
        admin_status: bool,
        session: AsyncSession,
    ) -> None:
        """
        Устанавливает в поле is_atmin пользователя в True или False.
        Аргументы:
            group_id - id чата
            user_id - id пользователя
        """
        await session.execute(
            update(self.model)
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.group_id == group_id,
                )
            )
            .values(is_admin=admin_status)
        )
        await session.commit()

    async def update_status_rceive_newsletter(
        self,
        group_id: int,
        user_id: int,
        status: bool,
        session: AsyncSession,
    ) -> None:
        """
        Устанавливает в поле rceive_newsletter пользователя в True или False.
        Аргументы:
            group_id - id чата
            user_id - id пользователя
            status - статус рассылки
        """
        await session.execute(
            update(self.model)
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.group_id == group_id,
                )
            )
            .values(rceive_newsletter=status)
        )
        await session.commit()

    async def get_chat_where_user_admin(
        self,
        user_id: int,
        session: AsyncSession,
    ) -> UserGroupAssociation | None:
        """
        Возвращает чат, где пользователь является администратором.
        Аргументы:
        user_id  - id пользователя
        Возвращает:
            chat: Group | None
        """
        chat_where_user_admin: UserGroupAssociation | None = await session.execute(
            select(self.model)
            .options(
                selectinload(self.model.group)
            )  # для получения связаных данных из модели user
            .where(
                and_(
                    self.model.user_id == user_id,
                    self.model.is_admin,
                )
            )
        )
        return chat_where_user_admin.scalars().all()


# Дописать добавление пользователя в базу
# async def add_user_to_db(
#     self,
#     chat: types.Chat,
#     user: types.ChatMember,
#     session: AsyncSession,
# ) -> None:
#     # Из базы получаем объект группы из которой делается запрос
#     # Если его нет, добавляем в базу
#     group: Group | None = await session.execute(
#         select(Group).where(Group.group_id == chat.id)
#     )
#     group = group.scalars().first()
#     # Перебираем список пользователей и проверяем нет ли их в базе
#     # Если нет добавляем

#     # в объекте user_info словарь, получаем значения по ключам
#     user = await user_crud.create(
#         {
#             'user_id': user.user_id,
#             'user_name': user.username,
#             'first_name': user.first_name,
#             'last_name': user.last_name,
#         },
#         session,
#     )
#     # Проверяем нет ли в базе связки пользователь группа
#     # если нет добавляем
#     user_group_association: (
#         UserGroupAssociation | None
#     ) = await crud_user_group_association.get_user_from_chat(
#         group_id=chat.id,
#         user_id=user_info['user_id'],
#         session=session,
#     )
#     if not user_group_association:
#         is_admin: bool = user_info['is_admin_or_creator']
#         association: UserGroupAssociation = UserGroupAssociation(
#             user=user, group=group, is_admin=is_admin
#         )
#         session.add(association)
#     await session.commit()


crud_user_group_association = CRUDUserGroupAssociation(UserGroupAssociation)
