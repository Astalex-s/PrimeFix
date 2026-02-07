"""Pydantic-схемы для заявок."""
from datetime import datetime

from pydantic import BaseModel


class LeadBase(BaseModel):
    name: str
    surname: str
    patronymic: str | None = None
    business_info: str | None = None
    budget: str | None = None
    contact_method: str | None = None
    comments: str | None = None
    niche: str | None = None
    company_size: str | None = None
    task_volume: str | None = None
    role: str | None = None
    business_size: str | None = None
    need_volume: str | None = None
    deadline: str | None = None
    task_type: str | None = None
    product_interest: str | None = None
    preferred_contact_method: str | None = None
    convenient_time: str | None = None
    service: str | None = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    name: str | None = None
    surname: str | None = None
    patronymic: str | None = None
    business_info: str | None = None
    budget: str | None = None
    contact_method: str | None = None
    comments: str | None = None
    niche: str | None = None
    company_size: str | None = None
    task_volume: str | None = None
    role: str | None = None
    business_size: str | None = None
    need_volume: str | None = None
    deadline: str | None = None
    task_type: str | None = None
    product_interest: str | None = None
    preferred_contact_method: str | None = None
    convenient_time: str | None = None
    service: str | None = None


class LeadResponse(LeadBase):
    id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True
