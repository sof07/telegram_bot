from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.crud.user_group_association import crud_user_group_association
from sqlalchemy.ext.asyncio import AsyncSession


router = Router()


@router.callback_query(F.data.startswith('chat_'))
async def callbacks_chat(callback: types.CallbackQuery) -> None:
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
