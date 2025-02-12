from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import extract

from app.crud.base import CRUDBase
from app.models import UserGroupAssociation
from app.models.user import User


class CRUDUser(CRUDBase):
    async def get_user(
        self,
        user_id: int,
        session: AsyncSession,
    ) -> None | User:
        user_obj = await session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return user_obj.scalars().first()

    async def get_users_and_groups_by_today_birthdays(
        self, session: AsyncSession
    ) -> list[tuple[User, int]]:
        """Получает список (пользователь, group_id) для пользователей с ДР сегодня."""
        today = date.today()

        stmt = (
            select(self.model, UserGroupAssociation.group_id)
            .join(self.model.groups)  # Джойним User -> UserGroupAssociation
            .where(
                extract('month', self.model.date_of_birth) == today.month,
                extract('day', self.model.date_of_birth) == today.day,
            )
        )
        result = await session.execute(stmt)
        data = result.all()
        print(f'Fetched users before commit: {data}')
        # <-- Принудительное сохранение изменений
        return data


user_crud = CRUDUser(User)
