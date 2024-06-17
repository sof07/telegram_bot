from app.models.group import Group
from app.crud.base import CRUDBase
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import user_crud
from sqlalchemy.future import select
from app.models.user import User
from app.models.user_group_association import UserGroupAssociation


class CRUDGroup(CRUDBase):
    async def add_chat_members_to_db(self, chat, user_data, session: AsyncSession):
        # Добавляем или получаем группу
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
        for user_info in user_data:
            user = await session.execute(
                select(User).where(User.user_id == user_info['user_id'])
            )
            user = user.scalars().first()
            if not user:
                user = await user_crud.create(
                    {
                        'user_id': user_info['user_id'],
                        'user_name': user_info['user_name'],
                        'first_name': user_info['first_name'],
                        'last_name': user_info['last_name'],
                    },
                    session,
                )
            is_admin = user_info['is_admin_or_creator']
            association = UserGroupAssociation(
                user=user, group=group, is_admin=is_admin
            )  # Тут сломалось после добавления is_admin
            session.add(association)
        await session.commit()


crud_group = CRUDGroup(Group)
