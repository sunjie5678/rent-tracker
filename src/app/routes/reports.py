"""Report routes."""

from flask import Blueprint, flash, redirect, render_template, url_for

from app.forms.report_forms import DateRangeForm, PropertyReportForm
from app.repositories.property_repository import PropertyRepository
from app.services.report_service import ReportService

bp = Blueprint("reports", __name__)


@bp.route("/")
def index():
    """Reports dashboard."""
    return render_template(
        "reports/dashboard.html",
    )


@bp.route("/arrears")
def arrears():
    """Arrears report."""
    service = ReportService()
    arrears_data = service.get_arrears_report()

    return render_template(
        "reports/arrears.html",
        arrears=arrears_data,
    )


@bp.route("/property/<int:property_id>")
def property_report(property_id: int):
    """Property payment history report."""
    service = ReportService()
    report = service.get_property_report(property_id)

    if not report:
        flash("Property not found.", "danger")
        return redirect(url_for("reports.index"))

    # Get timeline data
    timeline = service.get_payment_timeline(property_id)

    return render_template(
        "reports/property_history.html",
        report=report,
        timeline=timeline,
    )


@bp.route("/property", methods=["GET", "POST"])
def select_property():
    """Select property for report."""
    form = PropertyReportForm()

    if form.validate_on_submit():
        return redirect(
            url_for("reports.property_report", property_id=form.property_id.data)
        )

    return render_template(
        "reports/select_property.html",
        form=form,
    )


@bp.route("/financial", methods=["GET", "POST"])
def financial():
    """Financial summary report."""
    from datetime import date

    form = DateRangeForm()
    report = None

    if form.validate_on_submit():
        service = ReportService()
        report = service.get_financial_summary(
            start_date=form.start_date.data,
            end_date=form.end_date.data,
        )
    else:
        # Default to current year
        service = ReportService()
        report = service.get_financial_summary()

    return render_template(
        "reports/financial.html",
        form=form,
        report=report,
    )
