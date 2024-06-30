from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder


router = Router()


@router.callback_query(F.data.startswith('chat_'))
async def callbacks_chat(callback: types.CallbackQuery):
    messages = ['Получать', 'Не получать']
    action = callback.data.split('_')[1]
    builder = InlineKeyboardBuilder()
    for message in messages:
        builder.add(
            types.InlineKeyboardButton(
                text=str(message),
                callback_data=f'action_{message}',
            )
        )
    builder.adjust(2)
    await callback.message.edit_text(
        f'Ты хочешь получать сообщения из чата {action}\n'
        'Или отписаться от получения сообщений?',
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
    await callback.answer()


@router.callback_query(F.data.startswith('action_'))
async def callbacks_action_with_chat(callback: types.CallbackQuery):
    # здесь буду записывать в базу данных пожелание пользователя
    pass
