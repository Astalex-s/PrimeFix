"""Модель заявки (лид)."""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from backend.core.database import Base


class Lead(Base):
    """Таблица заявок от «тёплых» клиентов."""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    patronymic = Column(String(255), nullable=True)
    business_info = Column(Text, nullable=True)
    budget = Column(String(255), nullable=True)
    contact_method = Column(String(255), nullable=True)
    comments = Column(Text, nullable=True)
    niche = Column(String(255), nullable=True)
    company_size = Column(String(255), nullable=True)
    task_volume = Column(String(255), nullable=True)
    role = Column(String(100), nullable=True)
    business_size = Column(String(255), nullable=True)
    need_volume = Column(String(255), nullable=True)
    deadline = Column(String(255), nullable=True)
    task_type = Column(String(255), nullable=True)
    product_interest = Column(String(255), nullable=True)
    preferred_contact_method = Column(String(255), nullable=True)
    convenient_time = Column(String(255), nullable=True)
    service = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
