from app.core.db import Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship


class User(Base):
    user_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    groups = relationship('UserGroupAssociation', back_populates='user')
