"""Домен метрик поведения пользователей на сайте (трекинг, хитмэп)."""
from backend.behavior_metrics.model import BehaviorMetrics
from backend.behavior_metrics.router import router

__all__ = ["BehaviorMetrics", "router"]
