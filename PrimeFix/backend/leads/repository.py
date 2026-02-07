"""Репозиторий заявок (CRUD)."""
from sqlalchemy.orm import Session

from backend.leads.model import Lead


class LeadRepository:
    """CRUD-операции для Lead."""

    @staticmethod
    def create(db: Session, **kwargs) -> Lead:
        lead = Lead(**kwargs)
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead

    @staticmethod
    def get_by_id(db: Session, lead_id: int) -> Lead | None:
        return db.query(Lead).filter(Lead.id == lead_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Lead]:
        return db.query(Lead).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, lead_id: int, **kwargs) -> Lead | None:
        lead = LeadRepository.get_by_id(db, lead_id)
        if not lead:
            return None
        for key, value in kwargs.items():
            if hasattr(lead, key):
                setattr(lead, key, value)
        db.commit()
        db.refresh(lead)
        return lead

    @staticmethod
    def delete(db: Session, lead_id: int) -> bool:
        lead = LeadRepository.get_by_id(db, lead_id)
        if not lead:
            return False
        db.delete(lead)
        db.commit()
        return True
