"""Репозиторий админ-настроек (CRUD)."""
from sqlalchemy.orm import Session

from backend.admin.model import AdminSetting


class AdminSettingRepository:
    """CRUD-операции для AdminSetting."""

    @staticmethod
    def create(db: Session, key: str, value: str, **kwargs) -> AdminSetting:
        setting = AdminSetting(key=key, value=value, **kwargs)
        db.add(setting)
        db.commit()
        db.refresh(setting)
        return setting

    @staticmethod
    def get_by_id(db: Session, setting_id: int) -> AdminSetting | None:
        return db.query(AdminSetting).filter(AdminSetting.id == setting_id).first()

    @staticmethod
    def get_by_key(db: Session, key: str) -> AdminSetting | None:
        return db.query(AdminSetting).filter(AdminSetting.key == key).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[AdminSetting]:
        return db.query(AdminSetting).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, setting_id: int, **kwargs) -> AdminSetting | None:
        setting = AdminSettingRepository.get_by_id(db, setting_id)
        if not setting:
            return None
        for key, value in kwargs.items():
            if hasattr(setting, key):
                setattr(setting, key, value)
        db.commit()
        db.refresh(setting)
        return setting

    @staticmethod
    def delete(db: Session, setting_id: int) -> bool:
        setting = AdminSettingRepository.get_by_id(db, setting_id)
        if not setting:
            return False
        db.delete(setting)
        db.commit()
        return True
