from sqlalchemy import Column, Integer, String
from sqlalchemy.types import Date
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.db import Base


class User(Base):
    user_id = Column(Integer, unique=True)
    user_name = Column(String(100), nullable=True, default='Unknown')
    first_name = Column(String(100), nullable=True, default='Unknown')
    last_name = Column(String(100), nullable=True, default='Unknown')
    first_name_last_name = Column(
        String(100),
        nullable=True,
    )
    date_of_birth = Column(Date, nullable=True, default=None)
    groups = relationship(
        'UserGroupAssociation',
        back_populates='user',
        cascade='all, delete-orphan',  # Каскадное удаление связей при удалении пользователя
    )

    def __repr__(self):
        # При вывде объекта на печать. возвращает человекочитаемый текст о нем
        return self.user_name
