from aiogram import Router, types, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.services.services import chat_members
from app.crud.group import crud_group, crud_user_group_association
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UserGroupAssociation
from app.filters.filters import IsAdmin
from aiogram.utils import markdown
from aiogram.enums import ParseMode

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
    user_id: int = message.from_user.id
    # Список объектов класса UserGroupAssociation, где пользователь админ
    user_chat_admin: list[
        UserGroupAssociation
    ] = await crud_user_group_association.get_chat_where_user_admin(
        user_id=user_id, session=session
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
                    callback_data=f'faction_{action}_{user_id}',
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
            'Ты не админ ни в одной группе или не добавил бота в группу.\n'
            'Добавь бота в группу, назначь его администратором, а потом возвращайся.'
        )


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
    await message.answer('Здесь пока ничего нет, возможно скоро появится.')
