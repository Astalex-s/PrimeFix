"""
Модель услуги: отдельная строка в БД (название + описание).
Админ добавляет услуги по одной; пользователь выбирает из списка и видит описание.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from backend.core.database import Base


class Service(Base):
    """
    Таблица услуг для выбора в форме заявки.

    CREATE TABLE services (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ServiceCRUD:
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
        s = ServiceCRUD.get_by_id(db, service_id)
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
        s = ServiceCRUD.get_by_id(db, service_id)
        if not s:
            return False
        db.delete(s)
        db.commit()
        return True
