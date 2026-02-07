"""Роуты админа: CRUD услуг (каждая услуга — отдельная строка в таблице services)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.service import Service, ServiceCRUD
from backend.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter(prefix="/admin/services", tags=["admin", "services"])


@router.get("/", response_model=list[ServiceResponse])
def list_services(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    """Список всех услуг для админки."""
    return ServiceCRUD.get_all(db, skip=skip, limit=limit)


@router.post("/", response_model=ServiceResponse)
def create_service(data: ServiceCreate, db: Session = Depends(get_db)):
    """Добавить услугу (одна строка в БД)."""
    return ServiceCRUD.create(db, name=data.name, description=data.description)


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    s = ServiceCRUD.get_by_id(db, service_id)
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    return s


@router.patch("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: int, data: ServiceUpdate, db: Session = Depends(get_db)):
    s = ServiceCRUD.update(db, service_id, **data.model_dump(exclude_unset=True))
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    return s


@router.delete("/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    if not ServiceCRUD.delete(db, service_id):
        raise HTTPException(status_code=404, detail="Service not found")
