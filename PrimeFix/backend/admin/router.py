"""API-роуты для админ-настроек."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.admin.repository import AdminSettingRepository
from backend.admin.schema import AdminSettingCreate, AdminSettingResponse, AdminSettingUpdate
from backend.core.database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/", response_model=AdminSettingResponse)
def create_setting(data: AdminSettingCreate, db: Session = Depends(get_db)):
    existing = AdminSettingRepository.get_by_key(db, data.key)
    if existing:
        raise HTTPException(status_code=400, detail="Setting with this key already exists")
    return AdminSettingRepository.create(db, key=data.key, value=data.value)


@router.get("/", response_model=list[AdminSettingResponse])
def list_settings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return AdminSettingRepository.get_all(db, skip=skip, limit=limit)


@router.get("/key/{key}", response_model=AdminSettingResponse)
def get_setting_by_key(key: str, db: Session = Depends(get_db)):
    setting = AdminSettingRepository.get_by_key(db, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.get("/{setting_id}", response_model=AdminSettingResponse)
def get_setting(setting_id: int, db: Session = Depends(get_db)):
    setting = AdminSettingRepository.get_by_id(db, setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.patch("/{setting_id}", response_model=AdminSettingResponse)
def update_setting(setting_id: int, data: AdminSettingUpdate, db: Session = Depends(get_db)):
    setting = AdminSettingRepository.update(db, setting_id, **data.model_dump(exclude_unset=True))
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.delete("/{setting_id}", status_code=204)
def delete_setting(setting_id: int, db: Session = Depends(get_db)):
    if not AdminSettingRepository.delete(db, setting_id):
        raise HTTPException(status_code=404, detail="Setting not found")
