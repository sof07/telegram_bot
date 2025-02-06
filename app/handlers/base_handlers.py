from aiogram import Bot, F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt

from app.crud import crud_group, crud_user_group_association, user_crud
from app.filters.filters import IsAdmin
from app.models import UserGroupAssociation, User
from app.services.services import chat_members
from app.services.services import random_alphanumeric_string
import logging

router = Router()


# Обрабатывает команду /start, если она отправлена из чата
@router.message(
    CommandStart(),
    F.chat.type.in_({'group', 'supergroup', 'channel'}),
    IsAdmin(),
)
async def start_in_chat(message: types.Message, bot: Bot, session: AsyncSession):
    """
    Обрабатывает команду /start в группе, супергруппе или канале.

    :param message: Объект сообщения
    :param bot: Объект бота
    :param session: Асинхронная сессия SQLAlchemy
    """
    chat: types.Chat = message.chat
    user_data: list[dict] = await chat_members(chat.id)
    # Записывает пользователей в базу данных, связывая их с группой
    await crud_group.add_chat_members_to_db(
        chat=chat, user_data=user_data, session=session
    )


# Обрабатывает команду /start, если она отправлена в приватном чате
@router.message(
    CommandStart(),
    F.chat.type.in_({'private'}),
)
async def start_in_bot(message: types.Message, session: AsyncSession):
    """
    Обрабатывает команду /start в приватном чате.

    :param message: Объект сообщения
    :param session: Асинхронная сессия SQLAlchemy
    """
    # Список объектов класса UserGroupAssociation, где пользователь админ
    user_chat_admin: list[
        UserGroupAssociation
    ] = await crud_user_group_association.get_chat_where_user_admin(
        user_id=message.from_user.id, session=session
    )
    # Если список не пуст, получаю список чатов
    if user_chat_admin:
        faction: list[str] = [
            'Подписаться на рассылку',
            'Удалить из рассылки',
        ]
        builder = InlineKeyboardBuilder()
        for action in faction:
            builder.add(
                types.InlineKeyboardButton(
                    text=action,
                    callback_data=f'faction_{action}_{message.from_user.id}',
                )
            )
        builder.adjust(2)
        await message.answer(
            (
                'Выбери что ты хочешь сделать:\n'
                '👉 Подписаться на рассылку - в 19:50 бот будет присылать сообщения '
                'о пользователях которыене отписались в чат после 17:00\n\n'
                '👉 Удалить из рассылки - удалить пользователя из рассылки. '
                'Бот не будет указывать выбранного пользователя в рассылке, если он не отписался '
                'полезно когда сотрудник в чате, но работает в другом подразделении'
            ),
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await message.answer(
            '❗Ты не админ ни в одной группе или не добавил бота в группу.\n'
            'Добавь бота в группу, назначь его администратором, а потом возвращайся.'
        )


@router.message(
    Command('admin'),
    F.chat.type.in_({'private'}),
)
async def access_to_the_admin_panel(message: types.Message, session: AsyncSession):
    try:
        user_chat_admin: list[
            UserGroupAssociation
        ] = await crud_user_group_association.get_chat_where_user_admin(
            user_id=message.from_user.id, session=session
        )
        if user_chat_admin:
            user: User = await user_crud.get_user(
                user_id=message.from_user.id, session=session
            )
            password: str = random_alphanumeric_string(5)
            hash_password: str = bcrypt.hashpw(
                password.encode('utf-8'), bcrypt.gensalt()
            ).decode('utf-8')

            await user_crud.update(
                db_obj=user, obj_in={'password': hash_password}, session=session
            )
            await message.answer(
                f'Твой логин: {message.from_user.id}\n Пароль: {password}\n Ссылка на админку:'
            )
        await message.answer(
            '❗Ты не админ ни в одной группе или не добавил бота в группу.\n'
            'Добавь бота в группу, назначь его администратором, а потом возвращайся.'
        )
    except Exception as e:
        logging.error(e)


# Обрабатывает команду /help, если она отправлена в приватном чате
@router.message(
    Command('help'),
    F.chat.type.in_({'private'}),
)
async def help(message: types.Message, bot: Bot, session: AsyncSession):
    """
    Обрабатывает команду /help в приватном чате.

    :param message: Объект сообщения
    :param bot: Объект бота
    :param session: Асинхронная сессия SQLAlchemy
    """
    await message.answer(
        '❗С 17:00 до 19:50 бот отлавливает в группе сообщения с словом "порядок"\n\n'
        '❗В 19:50 бот отправляет список людей не написавших слово "порядок" админу группы, который подписался на рассылку'
    )
