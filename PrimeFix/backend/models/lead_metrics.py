"""
Модель метрик поведения пользователя на странице (1:1 с заявкой) и CRUD.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from backend.core.database import Base


class LeadMetrics(Base):
    """
    Таблица лид-метрик: время на странице, клики, зависания курсора, возвраты.
    Связь с заявкой один к одному (id заявки = id метрик).

    SQL для создания таблицы:

    CREATE TABLE lead_metrics (
        id INTEGER PRIMARY KEY REFERENCES leads(id) ON DELETE CASCADE,
        time_on_page_seconds NUMERIC(12, 2),
        buttons_clicked JSONB,
        cursor_hover_data JSONB,
        return_count INTEGER DEFAULT 0,
        raw_metrics JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    __tablename__ = "lead_metrics"

    id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), primary_key=True)
    time_on_page_seconds = Column(String(50), nullable=True)
    buttons_clicked = Column(Text, nullable=True)
    cursor_hover_data = Column(Text, nullable=True)
    return_count = Column(Integer, default=0)
    raw_metrics = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class LeadMetricsCRUD:
    """CRUD-операции для модели LeadMetrics."""

    @staticmethod
    def create(db: Session, lead_id: int, **kwargs) -> LeadMetrics:
        metrics = LeadMetrics(id=lead_id, **kwargs)
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
        return metrics

    @staticmethod
    def get_by_lead_id(db: Session, lead_id: int) -> LeadMetrics | None:
        return db.query(LeadMetrics).filter(LeadMetrics.id == lead_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[LeadMetrics]:
        return db.query(LeadMetrics).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, lead_id: int, **kwargs) -> LeadMetrics | None:
        metrics = LeadMetricsCRUD.get_by_lead_id(db, lead_id)
        if not metrics:
            return None
        for key, value in kwargs.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)
        db.commit()
        db.refresh(metrics)
        return metrics

    @staticmethod
    def delete(db: Session, lead_id: int) -> bool:
        metrics = LeadMetricsCRUD.get_by_lead_id(db, lead_id)
        if not metrics:
            return False
        db.delete(metrics)
        db.commit()
        return True
