"""API админа: CRUD услуг."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.repository import ServiceRepository
from backend.services.schema import ServiceCreate, ServiceResponse, ServiceUpdate

router = APIRouter(prefix="/admin/services", tags=["admin", "services"])


@router.get("/", response_model=list[ServiceResponse])
def list_services(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    return ServiceRepository.get_all(db, skip=skip, limit=limit)


@router.post("/", response_model=ServiceResponse)
def create_service(data: ServiceCreate, db: Session = Depends(get_db)):
    return ServiceRepository.create(db, name=data.name, description=data.description)


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    s = ServiceRepository.get_by_id(db, service_id)
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    return s


@router.patch("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: int, data: ServiceUpdate, db: Session = Depends(get_db)):
    s = ServiceRepository.update(db, service_id, **data.model_dump(exclude_unset=True))
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    return s


@router.delete("/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    if not ServiceRepository.delete(db, service_id):
        raise HTTPException(status_code=404, detail="Service not found")
