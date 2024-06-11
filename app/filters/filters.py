from aiogram.filters import BaseFilter
from aiogram import types


# class IsAdmin(BaseFilter):
#     async def __call__(self, message: types.Message) -> bool:
#         member = await message.bot.get_chat_member(
#             message.chat.id, message.from_user.id
#         )
#         return (
#             str(member.status) == 'ChatMemberStatus.CREATOR'
#         )  # Переделать. это костыль


class IsAdmin(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        member = await message.bot.get_chat_member(
            message.chat.id, message.from_user.id
        )
        return member.status in ['administrator', 'creator']
