"""Flask routes (blueprints)."""

from app.routes.allocations import bp as allocations_bp
from app.routes.dashboard import bp as dashboard_bp
from app.routes.payments import bp as payments_bp
from app.routes.properties import bp as properties_bp
from app.routes.reports import bp as reports_bp
from app.routes.tenants import bp as tenants_bp

__all__ = [
    "dashboard_bp",
    "properties_bp",
    "tenants_bp",
    "payments_bp",
    "allocations_bp",
    "reports_bp",
]
