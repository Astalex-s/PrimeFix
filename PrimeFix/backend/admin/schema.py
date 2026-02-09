"""Pydantic-схемы для админ-настроек."""
from datetime import datetime

from pydantic import BaseModel


class AdminSettingBase(BaseModel):
    key: str
    value: str


class AdminSettingCreate(AdminSettingBase):
    pass


class AdminSettingUpdate(BaseModel):
    key: str | None = None
    value: str | None = None


class AdminSettingResponse(AdminSettingBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
