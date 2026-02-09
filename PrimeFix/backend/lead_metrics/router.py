"""API-роуты для метрик поведения.

POST и PATCH — публичные (трекер на главной странице).
GET и DELETE — защищены JWT (только для администратора).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_admin
from backend.auth.model import Admin
from backend.core.database import get_db
from backend.lead_metrics.repository import LeadMetricsRepository
from backend.lead_metrics.schema import (
    LeadMetricsCreate,
    LeadMetricsResponse,
    LeadMetricsUpdate,
)

router = APIRouter(prefix="/lead-metrics", tags=["lead-metrics"])


# ── Публичные эндпоинты (трекер) ────────────────────────────────────


@router.post("/", response_model=LeadMetricsResponse)
def create_lead_metrics(
    data: LeadMetricsCreate,
    db: Session = Depends(get_db),
):
    """Создание записи метрик (первый запрос от трекера)."""
    return LeadMetricsRepository.create(db, **data.model_dump())


@router.patch("/{metrics_id}", response_model=LeadMetricsResponse)
def update_lead_metrics(
    metrics_id: int,
    data: LeadMetricsUpdate,
    db: Session = Depends(get_db),
):
    """Обновление метрик (последующие запросы от трекера)."""
    metrics = LeadMetricsRepository.update(
        db, metrics_id, **data.model_dump(exclude_unset=True)
    )
    if not metrics:
        raise HTTPException(status_code=404, detail="Lead metrics not found")
    return metrics


# ── Защищённые эндпоинты (админ-панель) ─────────────────────────────


@router.get("/", response_model=list[LeadMetricsResponse])
def list_lead_metrics(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Список всех записей метрик (для хитмэпа и дашборда)."""
    return LeadMetricsRepository.get_all(db, skip=skip, limit=limit)


@router.get("/{metrics_id}", response_model=LeadMetricsResponse)
def get_lead_metrics(
    metrics_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Получение метрик по ID."""
    metrics = LeadMetricsRepository.get_by_id(db, metrics_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Lead metrics not found")
    return metrics


@router.delete("/{metrics_id}", status_code=204)
def delete_lead_metrics(
    metrics_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Удаление метрик."""
    if not LeadMetricsRepository.delete(db, metrics_id):
        raise HTTPException(status_code=404, detail="Lead metrics not found")
