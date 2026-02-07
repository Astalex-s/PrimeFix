"""Домен админ-настроек (key-value)."""
from backend.admin.model import AdminSetting
from backend.admin.router import router

__all__ = ["AdminSetting", "router"]
