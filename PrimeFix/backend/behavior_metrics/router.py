"""API-роуты для поведенческих метрик.

POST и PATCH — публичные (трекер на главной странице).
GET и DELETE — защищены JWT (только для администратора).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_admin
from backend.auth.model import Admin
from backend.behavior_metrics.repository import BehaviorMetricsRepository
from backend.behavior_metrics.schema import (
    BehaviorMetricsCreate,
    BehaviorMetricsResponse,
    BehaviorMetricsUpdate,
)
from backend.core.database import get_db

router = APIRouter(prefix="/behavior-metrics", tags=["behavior-metrics"])


# ── Публичные эндпоинты (трекер) ────────────────────────────────────


@router.post("/", response_model=BehaviorMetricsResponse)
def create_behavior_metrics(
    data: BehaviorMetricsCreate,
    db: Session = Depends(get_db),
):
    """Создание новой сессии метрик (первый запрос от трекера)."""
    return BehaviorMetricsRepository.create(db, **data.model_dump())


@router.patch("/{metrics_id}", response_model=BehaviorMetricsResponse)
def update_behavior_metrics(
    metrics_id: int,
    data: BehaviorMetricsUpdate,
    db: Session = Depends(get_db),
):
    """Обновление метрик сессии (последующие запросы от трекера)."""
    metrics = BehaviorMetricsRepository.update(
        db, metrics_id, **data.model_dump(exclude_unset=True)
    )
    if not metrics:
        raise HTTPException(status_code=404, detail="Behavior metrics not found")
    return metrics


# ── Защищённые эндпоинты (админ-панель) ─────────────────────────────


@router.get("/", response_model=list[BehaviorMetricsResponse])
def list_behavior_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Список всех сессий метрик (для админки / хитмэпа)."""
    return BehaviorMetricsRepository.get_all(db, skip=skip, limit=limit)


@router.get("/{metrics_id}", response_model=BehaviorMetricsResponse)
def get_behavior_metrics(
    metrics_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Получение конкретной сессии метрик."""
    metrics = BehaviorMetricsRepository.get_by_id(db, metrics_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Behavior metrics not found")
    return metrics


@router.delete("/{metrics_id}", status_code=204)
def delete_behavior_metrics(
    metrics_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Удаление сессии метрик."""
    if not BehaviorMetricsRepository.delete(db, metrics_id):
        raise HTTPException(status_code=404, detail="Behavior metrics not found")
