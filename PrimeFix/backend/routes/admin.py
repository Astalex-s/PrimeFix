"""Роуты для админ-настроек (услуги, бюджет и т.д.)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.admin import AdminSetting, AdminSettingCRUD
from backend.schemas.admin import AdminSettingCreate, AdminSettingUpdate, AdminSettingResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/", response_model=AdminSettingResponse)
def create_setting(data: AdminSettingCreate, db: Session = Depends(get_db)):
    existing = AdminSettingCRUD.get_by_key(db, data.key)
    if existing:
        raise HTTPException(status_code=400, detail="Setting with this key already exists")
    return AdminSettingCRUD.create(db, key=data.key, value=data.value)


@router.get("/", response_model=list[AdminSettingResponse])
def list_settings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return AdminSettingCRUD.get_all(db, skip=skip, limit=limit)


@router.get("/key/{key}", response_model=AdminSettingResponse)
def get_setting_by_key(key: str, db: Session = Depends(get_db)):
    setting = AdminSettingCRUD.get_by_key(db, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.get("/{setting_id}", response_model=AdminSettingResponse)
def get_setting(setting_id: int, db: Session = Depends(get_db)):
    setting = AdminSettingCRUD.get_by_id(db, setting_id)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.patch("/{setting_id}", response_model=AdminSettingResponse)
def update_setting(setting_id: int, data: AdminSettingUpdate, db: Session = Depends(get_db)):
    setting = AdminSettingCRUD.update(db, setting_id, **data.model_dump(exclude_unset=True))
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.delete("/{setting_id}", status_code=204)
def delete_setting(setting_id: int, db: Session = Depends(get_db)):
    if not AdminSettingCRUD.delete(db, setting_id):
        raise HTTPException(status_code=404, detail="Setting not found")
