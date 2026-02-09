"""Pydantic-схемы для поведенческих метрик."""
from datetime import datetime

from pydantic import BaseModel


class BehaviorMetricsCreate(BaseModel):
    """Создание записи метрик (первый POST от трекера)."""

    application_id: int = 0
    time_on_page: int = 0
    buttons_clicked: str = ""
    cursor_positions: str = ""
    return_frequency: int = 0


class BehaviorMetricsUpdate(BaseModel):
    """Обновление записи метрик (последующие PATCH от трекера)."""

    time_on_page: int | None = None
    buttons_clicked: str | None = None
    cursor_positions: str | None = None
    return_frequency: int | None = None


class BehaviorMetricsResponse(BaseModel):
    """Ответ с данными метрик."""

    id: int
    application_id: int
    time_on_page: int
    buttons_clicked: str | None = None
    cursor_positions: str | None = None
    return_frequency: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
