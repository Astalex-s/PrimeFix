"""API-роуты для заявок.

GET /leads/scored/ — защищённый JWT, возвращает лиды с анализом,
отсортированные по температуре (горячие первыми).
Остальные эндпоинты — публичные (форма заявки).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_admin
from backend.auth.model import Admin
from backend.core.database import get_db
from backend.leads.repository import LeadRepository
from backend.leads.schema import (
    LeadCreate,
    LeadResponse,
    LeadScoreInfo,
    LeadScoredResponse,
    LeadUpdate,
)
from backend.leads.scoring import score_lead

router = APIRouter(prefix="/leads", tags=["leads"])


# ── Публичные ────────────────────────────────────────────────────────


@router.post("/", response_model=LeadResponse)
def create_lead(data: LeadCreate, db: Session = Depends(get_db)):
    """Создание новой заявки (форма на сайте)."""
    return LeadRepository.create(db, **data.model_dump())


# ── Защищённые (JWT) ─────────────────────────────────────────────────


@router.get("/scored/", response_model=list[LeadScoredResponse])
def list_scored_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    """Список лидов с интеллектуальным анализом (горячие первыми)."""
    leads = LeadRepository.get_all(db, skip=0, limit=500)

    scored = []
    for lead in leads:
        sc = score_lead(lead)
        lead_dict = LeadResponse.model_validate(lead).model_dump()
        lead_dict["scoring"] = LeadScoreInfo(
            score=sc.score,
            temperature=sc.temperature,
            priority=sc.priority,
            needs_personal_manager=sc.needs_personal_manager,
            department=sc.department,
            summary=sc.summary,
        )
        scored.append(lead_dict)

    # Сортировка: горячие первыми
    scored.sort(key=lambda x: x["scoring"].score, reverse=True)
    return scored[skip : skip + limit]


@router.get("/", response_model=list[LeadResponse])
def list_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Список заявок (без скоринга)."""
    return LeadRepository.get_all(db, skip=skip, limit=limit)


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = LeadRepository.get_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
def update_lead(lead_id: int, data: LeadUpdate, db: Session = Depends(get_db)):
    lead = LeadRepository.update(db, lead_id, **data.model_dump(exclude_unset=True))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.delete("/{lead_id}", status_code=204)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    if not LeadRepository.delete(db, lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")
