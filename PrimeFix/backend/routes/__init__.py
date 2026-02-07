from backend.routes.leads import router as leads_router
from backend.routes.lead_metrics import router as lead_metrics_router
from backend.routes.admin import router as admin_router
from backend.routes.admin_services import router as admin_services_router
from backend.routes.services import router as services_router

__all__ = [
    "leads_router", "lead_metrics_router", "admin_router",
    "admin_services_router", "services_router",
]
