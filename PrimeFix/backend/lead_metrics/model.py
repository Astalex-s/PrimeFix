"""Модель метрик поведения пользователя (1:1 с заявкой)."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from backend.core.database import Base


class LeadMetrics(Base):
    """Таблица лид-метрик: время на странице, клики, зависания курсора, возвраты."""

    __tablename__ = "lead_metrics"

    id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), primary_key=True)
    time_on_page_seconds = Column(String(50), nullable=True)
    buttons_clicked = Column(Text, nullable=True)
    cursor_hover_data = Column(Text, nullable=True)
    return_count = Column(Integer, default=0)
    raw_metrics = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

