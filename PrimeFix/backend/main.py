"""
PrimeFix API — точка входа приложения.
Доступ к API только через Nginx (проксирует /api/ на backend:8080).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.database import Base, engine
from backend.db.migrations import run_migrations

# Импорт роутеров
from backend.auth.router import router as auth_router
from backend.leads.router import router as leads_router
from backend.lead_metrics.router import router as lead_metrics_router
from backend.services.router import router as services_router
from backend.services.admin_router import router as admin_services_router

# Импорт моделей для регистрации в SQLAlchemy metadata
import backend.auth.model  # noqa: F401
import backend.lead_metrics.model  # noqa: F401
import backend.leads.model  # noqa: F401
import backend.services.model  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создание таблиц и применение миграций при старте."""
    Base.metadata.create_all(bind=engine)
    run_migrations(engine)
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

# Регистрация роутеров
app.include_router(auth_router, prefix="/api")
app.include_router(leads_router, prefix="/api")
app.include_router(lead_metrics_router, prefix="/api")
app.include_router(services_router, prefix="/api")
app.include_router(admin_services_router, prefix="/api")


@app.get("/api/health")
def health():
    """Проверка работоспособности приложения."""
    return {"status": "ok"}
