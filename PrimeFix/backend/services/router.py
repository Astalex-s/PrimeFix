"""Публичный API: список услуг для формы заявки."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.repository import ServiceRepository
from backend.services.schema import ServicePublic

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/", response_model=list[ServicePublic])
def list_services(db: Session = Depends(get_db)):
    """Вернуть все услуги для выбора в форме."""
    return ServiceRepository.get_all(db, skip=0, limit=500)

