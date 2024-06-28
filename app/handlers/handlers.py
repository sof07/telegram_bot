from aiogram import Router, types, F


from app.crud.user_group_association import crud_user_group_association
from sqlalchemy.ext.asyncio import AsyncSession


router = Router()


@router.message(F.text.contains('Порядок') | F.text.contains('порядок'))
async def message_photo_caption_please(
    message: types.Message, session: AsyncSession
) -> None:
    group_id: int = message.chat.id
    user_id: int = message.from_user.id
    session = session
    await crud_user_group_association.update_status_can_receive_messages_true(
        group_id,
        user_id,
        session,
    )
