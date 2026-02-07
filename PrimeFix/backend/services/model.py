"""Модель услуги (справочник для формы заявки)."""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from backend.core.database import Base


class Service(Base):
    """Таблица услуг для выбора в форме заявки."""

    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
