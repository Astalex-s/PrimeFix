"""Модель метрик поведения пользователя на странице."""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from backend.core.database import Base


class LeadMetrics(Base):
    """Таблица метрик: время на странице, клики, позиции курсора, возвраты.

    Может быть привязана к заявке (lead_id) или существовать как
    самостоятельная запись трекера поведения (lead_id = NULL).
    """

    __tablename__ = "lead_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(
        Integer,
        ForeignKey("leads.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    time_on_page_seconds = Column(Integer, default=0, nullable=False)
    buttons_clicked = Column(Text, nullable=True)
    cursor_hover_data = Column(Text, nullable=True)
    return_count = Column(Integer, default=0, nullable=False)
    raw_metrics = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
