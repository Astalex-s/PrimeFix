"""
Модель админ-данных (услуги, диапазоны бюджета для фронта) и CRUD.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from backend.core.database import Base


class AdminSetting(Base):
    """
    Таблица настроек для админки: услуги, диапазоны бюджета и т.п.
    Фронт по этим данным формирует интерфейс (слайдер бюджета, список услуг).

    SQL для создания таблицы:

    CREATE TABLE admin_settings (
        id SERIAL PRIMARY KEY,
        key VARCHAR(100) UNIQUE NOT NULL,
        value TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    __tablename__ = "admin_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AdminSettingCRUD:
    """CRUD-операции для модели AdminSetting."""

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
        setting = AdminSettingCRUD.get_by_id(db, setting_id)
        if not setting:
            return None
        for key, value in kwargs.items():
            if hasattr(setting, key):
                setattr(setting, key, value)
        db.commit()
        db.refresh(setting)
        return setting

    @staticmethod
    def update_by_key(db: Session, key: str, value: str) -> AdminSetting | None:
        setting = AdminSettingCRUD.get_by_key(db, key)
        if not setting:
            return None
        setting.value = value
        db.commit()
        db.refresh(setting)
        return setting

    @staticmethod
    def delete(db: Session, setting_id: int) -> bool:
        setting = AdminSettingCRUD.get_by_id(db, setting_id)
        if not setting:
            return False
        db.delete(setting)
        db.commit()
        return True
