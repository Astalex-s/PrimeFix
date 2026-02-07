"""
Модель заявки (лид) и CRUD-операции.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from backend.core.database import Base


class Lead(Base):
    """
    Таблица заявок от «тёплых» клиентов.

    SQL для создания таблицы:

    CREATE TABLE leads (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        surname VARCHAR(255) NOT NULL,
        patronymic VARCHAR(255),
        business_info TEXT,
        budget VARCHAR(255),
        contact_method VARCHAR(255),
        comments TEXT,
        niche VARCHAR(255),
        company_size VARCHAR(255),
        task_volume VARCHAR(255),
        role VARCHAR(100),
        business_size VARCHAR(255),
        need_volume VARCHAR(255),
        deadline VARCHAR(255),
        task_type VARCHAR(255),
        product_interest VARCHAR(255),
        preferred_contact_method VARCHAR(255),
        convenient_time VARCHAR(255),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    patronymic = Column(String(255), nullable=True)
    business_info = Column(Text, nullable=True)
    budget = Column(String(255), nullable=True)
    contact_method = Column(String(255), nullable=True)
    comments = Column(Text, nullable=True)
    niche = Column(String(255), nullable=True)
    company_size = Column(String(255), nullable=True)
    task_volume = Column(String(255), nullable=True)
    role = Column(String(100), nullable=True)
    business_size = Column(String(255), nullable=True)
    need_volume = Column(String(255), nullable=True)
    deadline = Column(String(255), nullable=True)
    task_type = Column(String(255), nullable=True)
    product_interest = Column(String(255), nullable=True)
    preferred_contact_method = Column(String(255), nullable=True)
    convenient_time = Column(String(255), nullable=True)
    service = Column(String(255), nullable=True)  # выбранная услуга из справочника
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LeadCRUD:
    """CRUD-операции для модели Lead."""

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
        lead = LeadCRUD.get_by_id(db, lead_id)
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
        lead = LeadCRUD.get_by_id(db, lead_id)
        if not lead:
            return False
        db.delete(lead)
        db.commit()
        return True
