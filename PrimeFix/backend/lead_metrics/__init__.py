"""Домен метрик поведения лида."""
from backend.lead_metrics.model import LeadMetrics
from backend.lead_metrics.router import router

__all__ = ["LeadMetrics", "router"]
