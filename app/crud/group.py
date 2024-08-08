from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.crud.user import user_crud
from app.crud.user_group_association import crud_user_group_association
from app.models.group import Group
from app.models.user import User
from app.models.user_group_association import UserGroupAssociation


class CRUDGroup(CRUDBase):
    async def get_group(
        self,
        group_id: int,
        session: AsyncSession,
    ) -> None | Group:
        group_obj = await session.execute(
            select(self.model).where(self.model.group_id == group_id)
        )
        return group_obj.scalars().first()

    async def add_chat_members_to_db(
        self,
        chat: types.Chat,
        user_data: list[dict[str, str]],
        session: AsyncSession,
    ) -> None:
        # Из базы получаем объект группы из которой делается запрос
        # Если его нет, добавляем в базу
        group: Group | None = await session.execute(
            select(self.model).where(self.model.group_id == chat.id)
        )
        group = group.scalars().first()
        if not group:
            group = await self.create(
                {
                    'group_id': chat.id,
                    'group_name': chat.title if chat.title else 'Unknown',
                },
                session,
            )
        # Перебираем список пользователей и проверяем нет ли их в базе
        # Если нет добавляем
        for user_info in user_data:
            user: User | None = await user_crud.get_user(
                user_id=user_info['user_id'],
                session=session,
            )
            if not user:
                # в объекте user_info словарь, получаем значения по ключам
                user = await user_crud.create(
                    {
                        'user_id': user_info['user_id'],
                        'user_name': user_info['user_name'],
                        'first_name': user_info['first_name'],
                        'last_name': user_info['last_name'],
                    },
                    session,
                )
            # Проверяем нет ли в базе связки пользователь группа
            # если нет добавляем
            user_group_association: (
                UserGroupAssociation | None
            ) = await crud_user_group_association.get_user_from_chat(
                group_id=chat.id,
                user_id=user_info['user_id'],
                session=session,
            )
            if not user_group_association:
                is_admin: bool = user_info['is_admin_or_creator']
                association: UserGroupAssociation = UserGroupAssociation(
                    user=user, group=group, is_admin=is_admin
                )
                session.add(association)
        await session.commit()


crud_group = CRUDGroup(Group)
