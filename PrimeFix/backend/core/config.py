"""
Настройки приложения из переменных окружения.
Подключение к PostgreSQL берётся из docker-compose (сервис postgres).
"""
import os
from functools import lru_cache


@lru_cache
def get_settings():
    return type("Settings", (), {
        "DB_HOST": os.environ.get("DB_HOST", "postgres"),
        "DB_PORT": int(os.environ.get("DB_PORT", "5432")),
        "DB_NAME": os.environ.get("DB_NAME", "app_db"),
        "DB_USER": os.environ.get("DB_USER", "app_user"),
        "DB_PASSWORD": os.environ.get("DB_PASSWORD", "change_me"),
    })()


def get_database_url():
    s = get_settings()
    return (
        f"postgresql://{s.DB_USER}:{s.DB_PASSWORD}@{s.DB_HOST}:{s.DB_PORT}/{s.DB_NAME}"
    )
