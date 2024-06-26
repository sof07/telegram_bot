from aiogram import Router, types, Bot, F

from aiogram.filters import CommandStart, Command
from aiogram.filters.chat_member_updated import (
    IS_ADMIN,
    ChatMemberUpdatedFilter,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.services.services import chat_members
from app.crud.group import crud_group, crud_user_group_association
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UserGroupAssociation


router = Router()


# Обрабатывает команду /start если она отправлена из чата
@router.message(
    CommandStart(),
    F.chat.type.in_({'group', 'supergroup'}),
    # ChatMemberUpdatedFilter(
    #     # member_status_changed=IS_ADMIN
    # ),  # ДОРАБОТАТЬ ФИЛЬТР НА АДМИНА
)
async def start_in_chat(message: types.Message, bot: Bot, session: AsyncSession):
    chat: types.Chat = message.chat
    user_data: list[dict] = await chat_members(chat.id)
    # Записывает пользователей в базу данных связывая их с группой
    await crud_group.add_chat_members_to_db(
        chat=chat, user_data=user_data, session=session
    )


@router.message(
    CommandStart(),
    F.chat.type.in_({'private'}),
)
async def start_in_bot(
    message: types.Message,
    session: AsyncSession,
):
    user_id: int = message.from_user.id
    # Список объектов класса UserGroupAssociation где пользователь админ
    user_chat_admin: UserGroupAssociation = (
        await crud_user_group_association.get_chat_where_user_admin(
            user_id=user_id, session=session
        )
    )
    # Если список не пуст, получаю список чатов
    if user_chat_admin:
        chat_name_list: list[str] = [
            group.group.group_name for group in user_chat_admin
        ]
        # Создаю клавиатуру
        builder = InlineKeyboardBuilder()
        for chat_name in chat_name_list:
            builder.add(
                types.InlineKeyboardButton(
                    text=str(chat_name),
                    callback_data=f'chat_{chat_name}',
                )
            )
        builder.adjust(2)

        await message.answer(
            f'Группы в которых ты админ:\n{'\n'.join(chat_name_list)}\n\n'
            'Хочешь получать уведомления от бота?\n'
            'Выбери группу и нажми подписаться.\n\n'
            'Уведомления тебя достали?\n'
            'Выбери группу и нажми отписаться.',
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await message.answer(
            'Ты не админ ни в одной группе, либо не добавил бота в группу\n'
            'Добавь бота в группу, назначь его администратором, потом возвращайся'
        )


@router.message(
    Command('help'),
    F.chat.type.in_({'private'}),
    # ChatMemberUpdatedFilter(
    #     # member_status_changed=IS_ADMIN
    # ),  # ДОРАБОТАТЬ ФИЛЬТР НА АДМИНА
)
async def help(message: types.Message, bot: Bot, session: AsyncSession):
    await message.answer('Здесь пока ничего нет, возможно скоро появится.')
