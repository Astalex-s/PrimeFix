"""Публичный роут: список услуг для формы заявки (таблица services)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.service import ServiceCRUD
from backend.schemas.service import ServicePublic

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/", response_model=list[ServicePublic])
def list_services(db: Session = Depends(get_db)):
    """Вернуть все услуги из таблицы services (название + описание) для выбора в форме."""
    return ServiceCRUD.get_all(db, skip=0, limit=500)
