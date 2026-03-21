"""Report routes."""

from flask import Blueprint, flash, redirect, render_template, url_for

from app.config import is_email_configured
from app.forms.report_forms import DateRangeForm, PropertyReportForm
from app.repositories.tenant_repository import TenantRepository
from app.services.email_service import EmailService
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
        email_configured=is_email_configured(),
    )


@bp.route("/arrears/send-notice/<int:tenant_id>", methods=["POST"])
def send_arrears_notice(tenant_id: int):
    """Send arrears notice email to a tenant from the arrears report."""
    if not is_email_configured():
        flash("Email is not configured. Set Google Gmail API variables in .env.", "warning")
        return redirect(url_for("reports.arrears"))

    tenant_repo = TenantRepository()
    tenant = tenant_repo.get_by_id(tenant_id)
    if not tenant or not tenant.email:
        flash("Tenant not found or has no email address.", "danger")
        return redirect(url_for("reports.arrears"))

    service = ReportService()
    arrears_data = service.get_arrears_report()
    row = next((x for x in arrears_data if x["tenant"].id == tenant_id), None)
    if not row:
        flash("No arrears on record for this tenant.", "warning")
        return redirect(url_for("reports.arrears"))

    prop = row["property"]
    address = f"{prop.address}, {prop.city}"

    try:
        EmailService().send_arrears_notice(
            tenant_email=tenant.email,
            tenant_name=tenant.name,
            property_address=address,
            amount_owed=float(row["total_outstanding"]),
            days_overdue=row["days_overdue"],
        )
        flash(f"Arrears notice sent to {tenant.email}.", "success")
    except Exception as e:
        flash(f"Failed to send email: {e}", "danger")

    return redirect(url_for("reports.arrears"))


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
