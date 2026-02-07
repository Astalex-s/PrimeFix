"""Pydantic-схемы для услуг."""
from datetime import datetime
from pydantic import BaseModel


class ServiceBase(BaseModel):
    name: str
    description: str | None = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ServiceResponse(ServiceBase):
    id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class ServicePublic(BaseModel):
    """Для публичного API формы: id, название, описание."""
    id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True
