from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.db import AsyncSessionLocal
from app.crud import crud_group, crud_user_group_association
from app.models import Group, UserGroupAssociation
from app.services.services import send_message_to_admin

scheduler = AsyncIOScheduler()
# Запуск планировщика для выполнения задачи каждый день в 20:00


async def scheduled_task_send_message_to_admin(bot: Bot) -> None:
    """Отправляет список пользователей админу"""
    async with AsyncSessionLocal() as session:
        all_groups: list[Group] | None = await crud_group.get_multi(session)
        for group in all_groups:
            # Получаем список пользователей для рассылки сообщений
            admin_list: (
                list[UserGroupAssociation] | None
            ) = await crud_user_group_association.get_user_crceive_newsletter_status(
                group_id=group.group_id,
                rceive_newsletter_status=True,
                session=session,
            )
            # Получаем список пользователей, без админов
            user_list: (
                list[UserGroupAssociation] | None
            ) = await crud_user_group_association.get_user_canrecive_message_status(
                group_id=group.group_id,
                can_receive_messages_status=False,
                rceive_newsletter_status=False,
                not_included_in_report_status=False,
                session=session,
            )
            # Получаем список id админов
            list_admin_id: list[int] | None = [user.user.user_id for user in admin_list]
            # Получаем список id пользователей
            list_user_first_name: list[str] | None = [
                user.user.first_name for user in user_list
            ]
            # Отправляю админам сообщение со списком неотписавшихся пользователей
            await send_message_to_admin(
                admin_list=list_admin_id, user_list=list_user_first_name, bot=bot
            )


async def reset_can_receive_messages() -> None:
    async with AsyncSessionLocal() as session:
        await crud_user_group_association.update_all_can_receive_messages_false(
            session=session
        )
    print('YES')
