from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.callback_data.callback_data import CallbackData

START_ANALYTICS = 'Начать сбор аналитики'


def analytics_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=START_ANALYTICS,
        callback_data=CallbackData.CB_ANALYTICS_START,
    )
    return builder.as_markup()


kb_analytics = analytics_keyboard()
