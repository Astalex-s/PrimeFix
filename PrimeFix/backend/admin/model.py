"""Модель админ-настроек (услуги, диапазоны бюджета для фронта)."""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from backend.core.database import Base


class AdminSetting(Base):
    """Таблица настроек для админки: услуги, диапазоны бюджета и т.п."""

    __tablename__ = "admin_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
