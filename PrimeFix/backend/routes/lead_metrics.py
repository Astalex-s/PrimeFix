"""Роуты для метрик поведения лида."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.lead_metrics import LeadMetrics, LeadMetricsCRUD
from backend.schemas.lead_metrics import LeadMetricsCreate, LeadMetricsUpdate, LeadMetricsResponse

router = APIRouter(prefix="/lead-metrics", tags=["lead-metrics"])


@router.post("/{lead_id}", response_model=LeadMetricsResponse)
def create_lead_metrics(lead_id: int, data: LeadMetricsCreate, db: Session = Depends(get_db)):
    existing = LeadMetricsCRUD.get_by_lead_id(db, lead_id)
    if existing:
        raise HTTPException(status_code=400, detail="Metrics for this lead already exist")
    metrics = LeadMetricsCRUD.create(db, lead_id, **data.model_dump())
    return metrics


@router.get("/", response_model=list[LeadMetricsResponse])
def list_lead_metrics(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return LeadMetricsCRUD.get_all(db, skip=skip, limit=limit)


@router.get("/{lead_id}", response_model=LeadMetricsResponse)
def get_lead_metrics(lead_id: int, db: Session = Depends(get_db)):
    metrics = LeadMetricsCRUD.get_by_lead_id(db, lead_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Lead metrics not found")
    return metrics


@router.patch("/{lead_id}", response_model=LeadMetricsResponse)
def update_lead_metrics(lead_id: int, data: LeadMetricsUpdate, db: Session = Depends(get_db)):
    metrics = LeadMetricsCRUD.update(db, lead_id, **data.model_dump(exclude_unset=True))
    if not metrics:
        raise HTTPException(status_code=404, detail="Lead metrics not found")
    return metrics


@router.delete("/{lead_id}", status_code=204)
def delete_lead_metrics(lead_id: int, db: Session = Depends(get_db)):
    if not LeadMetricsCRUD.delete(db, lead_id):
        raise HTTPException(status_code=404, detail="Lead metrics not found")
