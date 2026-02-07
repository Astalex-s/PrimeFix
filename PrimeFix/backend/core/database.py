"""
Драйвер подключения к PostgreSQL.
Доступ к БД только через backend; параметры из docker-compose (сервис postgres).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.core.config import get_database_url

Base = declarative_base()
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Генератор сессии БД для FastAPI Depends."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
