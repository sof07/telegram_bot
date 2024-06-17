from app.core.db import Base
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship


class User(Base):
    user_id = Column(Integer, unique=True)
    user_name = Column(String(100), nullable=True, default='Unknown')
    first_name = Column(String(100), nullable=True, default='Unknown')
    last_name = Column(String(100), nullable=True, default='Unknown')
    groups = relationship('UserGroupAssociation', back_populates='user')
