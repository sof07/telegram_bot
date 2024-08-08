from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_group_association import crud_user_group_association
from app.models import UserGroupAssociation

router = Router()


def truncate_string_to_byte_length(input_string: str, max_byte_length: int = 64) -> str:
    """
    Обрезает строку до указанной максимальной длины в байтах, если это необходимо.
    Параметры:
    input_string (str): Строка, которую нужно проверить и обрезать.
    max_byte_length (int): Максимальная допустимая длина строки в байтах.
    Возвращает:
    str: Обрезанная строка, если она превышает заданную длину в байтах.
    """

    max_byte = max_byte_length
    while len(input_string.encode('utf-8')) >= max_byte_length:
        input_string = input_string[:max_byte]
        max_byte -= 1
    return input_string


@router.callback_query(F.data.startswith('faction_'))
async def callbacks_faction(
    callback: types.CallbackQuery,
    session: AsyncSession,
) -> None:
    action: str = callback.data.split('_')[1]
    user_id: int = callback.from_user.id
    if action == 'Подписаться на рассылку':
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
            call_back_text: str = f'chat_{chat_id}_{chat_name}'
            builder.add(
                types.InlineKeyboardButton(
                    text=str(chat_name),
                    callback_data=truncate_string_to_byte_length(call_back_text),
                )
            )
        builder.adjust(2)
        chat_name_list: list[str] = [chat[0] for chat in chat_list]
        await callback.message.answer(
            f'Группы, в которых ты админ:\n👉 {"\n👉 ".join(chat_name_list)}\n\n'
            'Хочешь получать уведомления от бота?\n'
            'Выбери группу и нажми "Да".\n\n'
            'Уведомления тебя достали?\n'
            'Выбери группу и нажми "Нет".',
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
        await callback.answer()
    else:
        await callback.answer(
            'Пока этот функционал не реализован, если будет необходим допилим🤨',
            show_alert=True,
        )
        await callback.answer()


@router.callback_query(F.data.startswith('chat_'))
async def callbacks_chat(callback: types.CallbackQuery) -> None:
    """
    Обрабатывает callback-запросы, начинающиеся с 'chat_'.

    Эта функция создает и отправляет инлайн-клавиатуру с вариантами
    получения или отказа от получения сообщений из конкретного чата.

    :param callback: Объект callback-запроса Telegram.
    """
    messages: list[str] = ['Да', 'Нет']
    chat_name: str = callback.data.split('_')[2]
    chat_id: int = callback.data.split('_')[1]
    builder = InlineKeyboardBuilder()
    for message in messages:
        call_back_text = f'act_{message}_{chat_id}_{chat_name}'
        builder.add(
            types.InlineKeyboardButton(
                text=str(message),
                callback_data=truncate_string_to_byte_length(call_back_text),
            )
        )
    builder.adjust(2)
    await callback.message.answer(
        f'Ты хочешь получать сообщения из чата {chat_name}?',
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
    await callback.answer()


@router.callback_query(F.data.startswith('act_'))
async def callbacks_action_with_chat(
    callback: types.CallbackQuery, session: AsyncSession
) -> None:
    action: str = callback.data.split('_')[1]  # Получать, не получать
    chat_name: str = callback.data.split('_')[3]
    chat_id: int = callback.data.split('_')[2]
    if action == 'Да':
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
    if action == 'Нет':
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
