"""Dashboard routes."""

from flask import Blueprint, render_template

from app.services.report_service import ReportService

bp = Blueprint("dashboard", __name__)


@bp.route("/")
def index():
    """Dashboard home page."""
    service = ReportService()
    summary = service.get_dashboard_summary()

    return render_template(
        "dashboard.html",
        summary=summary,
    )
