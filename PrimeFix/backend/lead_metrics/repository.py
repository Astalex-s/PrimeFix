"""Репозиторий метрик поведения (CRUD)."""
from sqlalchemy.orm import Session

from backend.lead_metrics.model import LeadMetrics


class LeadMetricsRepository:
    """CRUD-операции для LeadMetrics."""

    @staticmethod
    def create(db: Session, **kwargs) -> LeadMetrics:
        """Создание новой записи метрик."""
        metrics = LeadMetrics(**kwargs)
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
        return metrics

    @staticmethod
    def get_by_id(db: Session, metrics_id: int) -> LeadMetrics | None:
        """Получение метрик по ID."""
        return db.query(LeadMetrics).filter(LeadMetrics.id == metrics_id).first()

    @staticmethod
    def get_by_lead_id(db: Session, lead_id: int) -> LeadMetrics | None:
        """Получение метрик по ID заявки."""
        return db.query(LeadMetrics).filter(LeadMetrics.lead_id == lead_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 200) -> list[LeadMetrics]:
        """Получение всех записей метрик (новые первыми)."""
        return (
            db.query(LeadMetrics)
            .order_by(LeadMetrics.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update(db: Session, metrics_id: int, **kwargs) -> LeadMetrics | None:
        """Обновление метрик по ID."""
        metrics = LeadMetricsRepository.get_by_id(db, metrics_id)
        if not metrics:
            return None
        for key, value in kwargs.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)
        db.commit()
        db.refresh(metrics)
        return metrics

    @staticmethod
    def delete(db: Session, metrics_id: int) -> bool:
        """Удаление метрик по ID."""
        metrics = LeadMetricsRepository.get_by_id(db, metrics_id)
        if not metrics:
            return False
        db.delete(metrics)
        db.commit()
        return True
