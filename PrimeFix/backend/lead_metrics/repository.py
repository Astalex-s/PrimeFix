"""Репозиторий метрик лида (CRUD)."""
from sqlalchemy.orm import Session

from backend.lead_metrics.model import LeadMetrics


class LeadMetricsRepository:
    """CRUD-операции для LeadMetrics."""

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
        metrics = LeadMetricsRepository.get_by_lead_id(db, lead_id)
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
        metrics = LeadMetricsRepository.get_by_lead_id(db, lead_id)
        if not metrics:
            return False
        db.delete(metrics)
        db.commit()
        return True
