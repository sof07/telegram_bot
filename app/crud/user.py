from app.crud.base import CRUDBase
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


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


user_crud = CRUDUser(User)
