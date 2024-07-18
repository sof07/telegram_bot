from aiogram import types
from aiogram.filters import BaseFilter


class IsAdmin(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        member = await message.bot.get_chat_member(
            message.chat.id, message.from_user.id
        )
        if (
            str(member.status) == 'ChatMemberStatus.CREATOR'
            or str(member.status) == 'ChatMemberStatus.ADMINISTRATOR'
        ):
            return True
        else:
            await message.bot.send_message(
                chat_id=message.from_user.id,
                text=f'{message.from_user.full_name} Не надо тыкать кнопку, ты не админ в группе!',
            )
        # Переделать. это костыль
