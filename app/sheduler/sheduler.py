from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.crud import crud_user_group_association, crud_group
from app.core.db import AsyncSessionLocal
from app.models import Group, UserGroupAssociation
from app.services.services import send_message_to_admin
from aiogram import Bot


scheduler = AsyncIOScheduler()
# Запуск планировщика для выполнения задачи каждый день в 20:00


async def scheduled_task(bot: Bot) -> None:
    """Отправляет список пользователей админу"""
    async with AsyncSessionLocal() as session:
        all_groups: list[Group] | None = await crud_group.get_multi(session)
        for group in all_groups:
            admin_list: (
                list[UserGroupAssociation] | None
            ) = await crud_user_group_association.get_user_canrecive_message_status(
                group_id=group.group_id,
                status=False,
                is_admin=True,
                session=session,
            )
            user_list: (
                list[UserGroupAssociation] | None
            ) = await crud_user_group_association.get_user_canrecive_message_status(
                group_id=group.group_id,
                status=False,
                is_admin=False,
                session=session,
            )
            list_admin_id: list[int] | None = [user.user.user_id for user in admin_list]
            list_user_first_name: list[str] | None = [
                user.user.first_name for user in user_list
            ]
            await send_message_to_admin(
                admin_list=list_admin_id, user_list=list_user_first_name, bot=bot
            )
