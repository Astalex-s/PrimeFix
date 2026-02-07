"""API-роуты для заявок."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.leads.repository import LeadRepository
from backend.leads.schema import LeadCreate, LeadResponse, LeadUpdate

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("/", response_model=LeadResponse)
def create_lead(data: LeadCreate, db: Session = Depends(get_db)):
    return LeadRepository.create(db, **data.model_dump())


@router.get("/", response_model=list[LeadResponse])
def list_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
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
