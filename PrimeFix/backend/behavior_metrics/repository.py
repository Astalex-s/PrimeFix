"""Репозиторий поведенческих метрик (CRUD)."""
from sqlalchemy.orm import Session

from backend.behavior_metrics.model import BehaviorMetrics


class BehaviorMetricsRepository:
    """CRUD-операции для BehaviorMetrics."""

    @staticmethod
    def create(db: Session, **kwargs) -> BehaviorMetrics:
        metrics = BehaviorMetrics(**kwargs)
        db.add(metrics)
        db.commit()
        db.refresh(metrics)
        return metrics

    @staticmethod
    def get_by_id(db: Session, metrics_id: int) -> BehaviorMetrics | None:
        return db.query(BehaviorMetrics).filter(BehaviorMetrics.id == metrics_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 200) -> list[BehaviorMetrics]:
        return (
            db.query(BehaviorMetrics)
            .order_by(BehaviorMetrics.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update(db: Session, metrics_id: int, **kwargs) -> BehaviorMetrics | None:
        metrics = BehaviorMetricsRepository.get_by_id(db, metrics_id)
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
        metrics = BehaviorMetricsRepository.get_by_id(db, metrics_id)
        if not metrics:
            return False
        db.delete(metrics)
        db.commit()
        return True
