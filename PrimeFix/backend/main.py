"""
PrimeFix API — точка входа приложения.
Доступ к API только через Nginx (проксирует /api/ на backend:8080).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.admin.model import AdminSetting
from backend.core.database import Base, engine
from backend.lead_metrics.model import LeadMetrics
from backend.leads.model import Lead
from backend.leads.router import router as leads_router
from backend.lead_metrics.router import router as lead_metrics_router
from backend.admin.router import router as admin_router
from backend.services.admin_router import router as admin_services_router
from backend.services.model import Service
from backend.services.router import router as services_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создание таблиц при старте и миграция колонки service."""
    Base.metadata.create_all(bind=engine)
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS service VARCHAR(255)"))
    except Exception:
        pass
    yield


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
app.include_router(services_router, prefix="/api")
app.include_router(admin_services_router, prefix="/api")  # до admin — более специфичный путь
app.include_router(admin_router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
