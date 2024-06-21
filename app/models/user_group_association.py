from app.core.db import Base
from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


class UserGroupAssociation(Base):
    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'group_id',
            name='unique_user_group_association',
        ),
    )

    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    group_id = Column(Integer, ForeignKey('group.group_id'), nullable=False)
    is_admin = Column(Boolean, default=False)
    can_receive_messages = Column(Boolean, default=False)

    user = relationship(
        'User',
        back_populates='groups',
    )
    group = relationship(
        'Group',
        back_populates='users',
    )

    def __repr__(self):
        # При вывде объекта на печать. возвращает человекочитаемый текст о нем
        return f'Пользователь с id {self.user_id}, в группе с id {self.group_id}, admin: {self.is_admin}'
