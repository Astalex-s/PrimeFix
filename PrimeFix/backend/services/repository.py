"""Репозиторий услуг (CRUD)."""
from sqlalchemy.orm import Session

from backend.services.model import Service


class ServiceRepository:
    """CRUD-операции для Service."""

    @staticmethod
    def create(db: Session, name: str, description: str | None = None) -> Service:
        s = Service(name=name, description=description)
        db.add(s)
        db.commit()
        db.refresh(s)
        return s

    @staticmethod
    def get_by_id(db: Session, service_id: int) -> Service | None:
        return db.query(Service).filter(Service.id == service_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 500) -> list[Service]:
        return db.query(Service).order_by(Service.id).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, service_id: int, **kwargs) -> Service | None:
        s = ServiceRepository.get_by_id(db, service_id)
        if not s:
            return None
        for key, value in kwargs.items():
            if hasattr(s, key):
                setattr(s, key, value)
        db.commit()
        db.refresh(s)
        return s

    @staticmethod
    def delete(db: Session, service_id: int) -> bool:
        s = ServiceRepository.get_by_id(db, service_id)
        if not s:
            return False
        db.delete(s)
        db.commit()
        return True
