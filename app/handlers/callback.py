from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.crud.user_group_association import crud_user_group_association
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UserGroupAssociation


router = Router()


@router.callback_query(F.data.startswith('faction_'))
async def callbacks_faction(
    callback: types.CallbackQuery,
    session: AsyncSession,
) -> None:
    faction: str = callback.data.split('_')[1]
    user_id: int = callback.from_user.id
    if faction == 'Подписаться на рассылку':
        user_chat_admin: list[
            UserGroupAssociation
        ] = await crud_user_group_association.get_chat_where_user_admin(
            user_id=user_id, session=session
        )
        chat_list: list[list[str]] = [
            [group.group.group_name, group.group.group_id] for group in user_chat_admin
        ]
        # Создаю клавиатуру
        builder = InlineKeyboardBuilder()
        for chat in chat_list:
            chat_name: str = chat[0]
            chat_id: int = chat[1]
            builder.add(
                types.InlineKeyboardButton(
                    text=str(chat_name),
                    callback_data=f'chat_{chat_name}_{chat_id}',
                )
            )
        builder.adjust(2)
        chat_name_list: list[str] = [chat[0] for chat in chat_list]
        await callback.answer(
            f'Группы, в которых ты админ:\n👉 {"\n👉 ".join(chat_name_list)}\n\n'
            'Хочешь получать уведомления от бота?\n'
            'Выбери группу и нажми "подписаться".\n\n'
            'Уведомления тебя достали?\n'
            'Выбери группу и нажми "отписаться".',
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await callback.answer(
            'Пока этот функционал не реализован, если будет необходим допилим🤨',
            show_alert=True,
        )


@router.callback_query(F.data.startswith('chat_'))
async def callbacks_chat(callback: types.CallbackQuery) -> None:
    """
    Обрабатывает callback-запросы, начинающиеся с 'chat_'.

    Эта функция создает и отправляет инлайн-клавиатуру с вариантами
    получения или отказа от получения сообщений из конкретного чата.

    :param callback: Объект callback-запроса Telegram.
    """
    messages: list[str] = ['Получать', 'Не получать']
    chat_name: str = callback.data.split('_')[1]
    chat_id: int = callback.data.split('_')[2]
    builder = InlineKeyboardBuilder()
    for message in messages:
        builder.add(
            types.InlineKeyboardButton(
                text=str(message),
                callback_data=f'action_{message}_{chat_name}_{chat_id}',
            )
        )
    builder.adjust(2)
    await callback.message.edit_text(
        f'Ты хочешь получать сообщения из чата {chat_name}\n'
        'Или отписаться от получения сообщений?',
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
    await callback.answer()


@router.callback_query(F.data.startswith('action_'))
async def callbacks_action_with_chat(
    callback: types.CallbackQuery, session: AsyncSession
) -> None:
    action: str = callback.data.split('_')[1]  # Получать, не получать
    chat_name: str = callback.data.split('_')[2]
    chat_id: int = callback.data.split('_')[3]
    if action == 'Получать':
        await crud_user_group_association.update_status_rceive_newsletter(
            user_id=callback.from_user.id,
            group_id=chat_id,
            status=True,
            session=session,
        )
        await callback.answer(
            text=f'Ты подписался на рассылку из чата {chat_name}',
            show_alert=True,
        )
    if action == 'Не получать':
        await crud_user_group_association.update_status_rceive_newsletter(
            user_id=callback.from_user.id,
            group_id=chat_id,
            status=False,
            session=session,
        )
        await callback.answer(
            text=f'Ты отписался от рассылки из чата {chat_name}',
            show_alert=True,
        )
    # здесь буду записывать в базу данных пожелание пользователя
