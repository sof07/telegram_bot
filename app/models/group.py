from app.core.db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Group(Base):
    group_id = Column(Integer, unique=True, nullable=False)
    group_name = Column(String(100), nullable=False)
    users = relationship(
        'UserGroupAssociation',
        back_populates='group',
    )
