from app.models.group import Group
from app.crud.base import CRUDBase
from app.crud.user_group_association import crud_user_group_association
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import user_crud


class CRUDGroup(CRUDBase):
    async def add_chat_members_to_db(
        self, chat_id, chat_name, user_data, session: AsyncSession
    ):
        # Добавляем или получаем группу
        group = await self.get(chat_id, session)
        print(f'Проверяю группу {group}')
        if not group:
            group = await self.create(
                {'group_id': chat_id, 'group_name': chat_name}, session
            )

        # Добавляем пользователей и ассоциации
        print('---------------------')
        print(f'Список пользоватедей {user_data}')
        for user_info in user_data:
            user = await user_crud.get(user_info['user_id'], session)
            if not user:
                user = await user_crud.create(
                    {
                        'id': user_info['user_id'],
                        'user_name': user_info['user_name'],
                        'first_name': user_info['first_name'],
                        'last_name': user_info['last_name'],
                    },
                    session,
                )

            user_group_association = await crud_user_group_association.create(
                {
                    'user_id': user.id,
                    'group_id': group.id,
                    'is_admin': user_info['is_admin_or_creator'],
                },
                session,
            )

    pass


crud_group = CRUDGroup(Group)
