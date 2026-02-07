"""Домен услуг (справочник)."""
from backend.services.model import Service
from backend.services.router import router as services_router
from backend.services.admin_router import router as admin_services_router

__all__ = ["Service", "services_router", "admin_services_router"]
