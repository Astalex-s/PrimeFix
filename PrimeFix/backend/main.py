"""
FastAPI-приложение: объединение роутов и подключение к БД.
Сервис приватный: доступ только внутри сети (Nginx проксирует /api/ на backend:8080).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.core.database import engine, Base
from backend.routes import (
    leads_router,
    lead_metrics_router,
    admin_router,
    admin_services_router,
    services_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создание таблиц при старте приложения и миграции (добавление колонок при необходимости)."""
    Base.metadata.create_all(bind=engine)
    # Добавить колонку service в leads, если таблица уже существовала без неё
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS service VARCHAR(255)"))
    except Exception:
        pass  # таблица может ещё не существовать или колонка уже есть
    yield
    # при остановке можно закрыть пул и т.д.


app = FastAPI(
    title="PrimeFix API",
    description="Бэкенд для заявок и метрик",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads_router, prefix="/api")
app.include_router(lead_metrics_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(admin_services_router, prefix="/api")
app.include_router(services_router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
