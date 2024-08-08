from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.db import Base


class User(Base):
    user_id = Column(Integer, unique=True)
    user_name = Column(String(100), nullable=True, default='Unknown')
    first_name = Column(String(100), nullable=True, default='Unknown')
    last_name = Column(String(100), nullable=True, default='Unknown')
    groups = relationship(
        'UserGroupAssociation',
        back_populates='user',
        cascade='all, delete-orphan',  # Каскадное удаление связей при удалении пользователя
    )

    def __repr__(self):
        # При вывде объекта на печать. возвращает человекочитаемый текст о нем
        return f'Пользователь: {self.user_name}, id пользователя: {self.user_id}'
