"""Pydantic-схемы для метрик лида."""
from datetime import datetime

from pydantic import BaseModel


class LeadMetricsBase(BaseModel):
    time_on_page_seconds: str | None = None
    buttons_clicked: str | None = None
    cursor_hover_data: str | None = None
    return_count: int = 0
    raw_metrics: str | None = None


class LeadMetricsCreate(LeadMetricsBase):
    pass


class LeadMetricsUpdate(BaseModel):
    time_on_page_seconds: str | None = None
    buttons_clicked: str | None = None
    cursor_hover_data: str | None = None
    return_count: int | None = None
    raw_metrics: str | None = None


class LeadMetricsResponse(LeadMetricsBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
