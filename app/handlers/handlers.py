from aiogram import F, Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user_group_association import crud_user_group_association

router = Router()


@router.message(F.text.contains('Порядок') | F.text.contains('порядок'))
async def user_wrote_the_keyword(message: types.Message, session: AsyncSession) -> None:
    group_id: int = message.chat.id
    user_id: int = message.from_user.id
    session = session
    await crud_user_group_association.update_status_can_receive_messages_true(
        group_id,
        user_id,
        session,
    )
