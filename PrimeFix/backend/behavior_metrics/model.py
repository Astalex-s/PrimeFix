"""Модель метрик поведения пользователей на главной странице."""
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func

from backend.core.database import Base


class BehaviorMetrics(Base):
    """Таблица поведенческих метрик: время на странице, клики, позиции курсора."""

    __tablename__ = "behavior_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, default=0, nullable=False)
    time_on_page = Column(Integer, default=0, nullable=False)      # секунды
    buttons_clicked = Column(Text, nullable=True)                   # JSON-строка
    cursor_positions = Column(Text, nullable=True)                  # JSON-строка
    return_frequency = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
