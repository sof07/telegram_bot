from aiogram import Router, types, F, Bot

from aiogram.filters import CommandStart

# from app.sheduler.sheduler import scheduler
from app.services.services import chat_members, send_message_to_admin
from app.crud.group import crud_group
from app.crud.user_group_association import crud_user_group_association
from sqlalchemy.ext.asyncio import AsyncSession

# from app.keyboards.inline_keyboard import kb_analytics

router = Router()
user_list: dict[dict] = {}
check_user_list: list[int] = []  # Список пользователей которые отписались


@router.message(CommandStart())
async def start(message: types.Message, session: AsyncSession):
    chat: types.Chat = message.chat  # Объект чата из которого отправлена команда start
    # Функция возвращает список пользователей из чата
    user_data = await chat_members(chat.id)
    # Записывает пользователей в базу данных связывая их с группой
    await crud_group.add_chat_members_to_db(
        chat=chat, user_data=user_data, session=session
    )
    # user_canrecive_message = (
    #     await crud_user_group_association.get_user_canrecive_message_false(
    #         group_id=chat.id, session=session
    #     )
    # )
    # for user in user_canrecive_message:
    #     print(f'{user.user}, id -> ')
    # await crud_user_group_association.set_all_can_receive_messages_false(
    #     session=session
    # )
    # await send_message_to_admin(message=message, session=session)
    # await message.reply('Участники чата успешно сохранены в базу данных.')


@router.message(F.text.contains('Порядок') | F.text.contains('порядок'))
async def message_photo_caption_please(
    message: types.Message, session: AsyncSession
) -> None:
    group_id: int = message.chat.id
    user_id: int = message.from_user.id
    session = session
    await crud_user_group_association.update_status_can_receive_messages_true(
        group_id,
        user_id,
        session,
    )


# Админы:
# пользователи со статусом одмин могут получать сообщения со списком не отписавшихся
# админы могут отписатьсяся от получения сообщений
# админ может подписать админа на получения сообщений

# проблема получения айди чата во время выполнения шедулера
