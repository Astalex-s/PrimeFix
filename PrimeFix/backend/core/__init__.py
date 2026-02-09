"""Ядро приложения: конфигурация и подключение к БД."""
from backend.core.database import Base, SessionLocal, engine, get_db

__all__ = ["Base", "SessionLocal", "engine", "get_db"]
