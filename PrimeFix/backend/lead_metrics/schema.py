"""Pydantic-схемы для метрик поведения."""
from datetime import datetime

from pydantic import BaseModel


class LeadMetricsCreate(BaseModel):
    """Создание записи метрик (от трекера, lead_id опционален)."""

    lead_id: int | None = None
    time_on_page_seconds: int = 0
    buttons_clicked: str = ""
    cursor_hover_data: str = ""
    return_count: int = 0
    raw_metrics: str | None = None


class LeadMetricsUpdate(BaseModel):
    """Обновление метрик (трекер каждую секунду)."""

    time_on_page_seconds: int | None = None
    buttons_clicked: str | None = None
    cursor_hover_data: str | None = None
    return_count: int | None = None
    raw_metrics: str | None = None


class LeadMetricsResponse(BaseModel):
    """Ответ с данными метрик."""

    id: int
    lead_id: int | None = None
    time_on_page_seconds: int
    buttons_clicked: str | None = None
    cursor_hover_data: str | None = None
    return_count: int
    raw_metrics: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
