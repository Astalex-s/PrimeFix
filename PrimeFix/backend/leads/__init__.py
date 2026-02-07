"""Домен заявок (лидов)."""
from backend.leads.model import Lead
from backend.leads.router import router

__all__ = ["Lead", "router"]
