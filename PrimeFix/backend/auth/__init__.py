"""Модуль авторизации администраторов."""
from backend.auth.model import Admin
from backend.auth.router import router

__all__ = ["Admin", "router"]
