from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime

from app.core.db import Base


class Log(Base):
    level = Column(String(50), nullable=False)  # Уровень лога (INFO, ERROR и т.д.)
    message = Column(Text, nullable=False)  # Текст сообщения
    timestamp = Column(DateTime, default=datetime.utcnow)  # Время лога
