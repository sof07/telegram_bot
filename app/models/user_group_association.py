from app.core.db import Base
from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class UserGroupAssociation(Base):
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('group.id'), nullable=False)
    is_admin = Column(Boolean, default=False)
    can_receive_messages = Column(Boolean, default=False)

    user = relationship('User', back_populates='groups')
    group = relationship('Group', back_populates='users')
