from app.models.user_group_association import UserGroupAssociation
from app.crud.base import CRUDBase

from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.group import Group


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

    async def get_user_canrecive_message_false(
        self,
        group_id: int,
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
                and_(self.model.group_id == group_id, self.model.can_receive_messages)
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

    # async def create(
    #     self,
    #     user: User,
    #     group: Group,
    #     session: AsyncSession,
    #     is_admin: bool = False,
    # ):
    #     db_obj: UserGroupAssociation = self.model(
    #         user=user, group=group, is_admin=is_admin
    #     )

    #     session.add(db_obj)
    #     await session.commit()
    #     await session.refresh(db_obj)
    #     return db_obj


crud_user_group_association = CRUDUserGroupAssociation(UserGroupAssociation)
