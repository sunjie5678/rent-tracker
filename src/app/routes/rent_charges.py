"""Rent charge routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.config import is_email_configured
from app.forms.rent_charge_forms import RentChargeFilterForm, RentChargeForm
from app.models.rent_charge import ChargeStatus
from app.repositories.property_repository import PropertyRepository
from app.repositories.rent_charge_repository import RentChargeRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.email_service import EmailService
from app.services.payment_service import PaymentService

bp = Blueprint("rent_charges", __name__)


@bp.route("/")
def list_charges():
    """List all rent charges."""
    repo = RentChargeRepository()
    filter_form = RentChargeFilterForm(request.args)

    property_id = request.args.get("property_id", type=int)
    status = request.args.get("status")

    if property_id:
        charges = repo.get_by_property(property_id)
    elif status:
        charges = repo.get_by_status(ChargeStatus(status))
    else:
        charges = repo.get_all()

    # Get property names for display
    prop_repo = PropertyRepository()
    properties = {p.id: p for p in prop_repo.get_all()}

    return render_template(
        "rent_charges/list.html",
        charges=charges,
        properties=properties,
        filter_form=filter_form,
    )


@bp.route("/new", methods=["GET", "POST"])
def create():
    """Create new rent charge (for backfilling historical data)."""
    form = RentChargeForm()

    # Pre-populate property_id from query param if provided
    if request.method == "GET":
        property_id = request.args.get("property_id", type=int)
        if property_id:
            form.property_id.data = property_id

    if form.validate_on_submit():
        # Validate property selection
        if not form.property_id.data or form.property_id.data == 0:
            flash("Please select a property.", "danger")
        elif form.period_end.data < form.period_start.data:
            flash("Period end date must be after start date.", "danger")
        elif form.due_date.data < form.period_start.data:
            flash("Due date should be after period start.", "warning")
        else:
            repo = RentChargeRepository()
            data = {
                "property_id": form.property_id.data,
                "period_start": form.period_start.data,
                "period_end": form.period_end.data,
                "amount_due": float(form.amount_due.data),
                "due_date": form.due_date.data,
                "status": ChargeStatus.CHARGED,
            }
            charge = repo.create(data)

            # Auto-update status based on date
            service = PaymentService()
            service.update_charge_status(charge)

            # Notify active tenants by email (Gmail API), emphasizing due date
            if is_email_configured():
                prop_repo = PropertyRepository()
                prop = prop_repo.get_by_id(charge.property_id)
                if prop:
                    tenants = TenantRepository().get_active_by_property(charge.property_id)
                    with_email = [t for t in tenants if t.email]
                    sent = 0
                    try:
                        email_service = EmailService()
                        for tenant in with_email:
                            email_service.send_new_rent_charge_notice(
                                tenant_email=tenant.email,
                                tenant_name=tenant.name,
                                property_address=f"{prop.address}, {prop.city}",
                                amount_due=float(charge.amount_due),
                                due_date=charge.due_date,
                                period_start=charge.period_start,
                                period_end=charge.period_end,
                            )
                            sent += 1
                    except Exception as e:
                        flash(
                            f"Rent charge created, but email failed: {e}",
                            "warning",
                        )
                        return redirect(url_for("rent_charges.list_charges"))

                    if sent:
                        flash(
                            f"Rent charge created. Due date notice sent to {sent} tenant(s).",
                            "success",
                        )
                    else:
                        flash(
                            "Rent charge created. No tenant email on file for this property.",
                            "success",
                        )
                    return redirect(url_for("rent_charges.list_charges"))

            flash("Rent charge created successfully!", "success")
            return redirect(url_for("rent_charges.list_charges"))

    # Get property info for display
    property_obj = None
    if form.property_id.data:
        prop_repo = PropertyRepository()
        property_obj = prop_repo.get_by_id(int(form.property_id.data))

    return render_template(
        "rent_charges/create.html",
        form=form,
        property=property_obj,
    )


@bp.route("/<int:charge_id>")
def detail(charge_id: int):
    """Rent charge detail page."""
    repo = RentChargeRepository()
    charge = repo.get_with_allocations(charge_id)

    if not charge:
        flash("Rent charge not found.", "danger")
        return redirect(url_for("rent_charges.list_charges"))

    # Calculate remaining amount
    total_allocated = sum(a.amount for a in charge.payment_allocations)
    remaining = charge.amount_due - total_allocated

    return render_template(
        "rent_charges/detail.html",
        charge=charge,
        total_allocated=total_allocated,
        remaining=remaining,
    )


@bp.route("/<int:charge_id>/delete", methods=["POST"])
def delete(charge_id: int):
    """Delete rent charge."""
    repo = RentChargeRepository()
    charge = repo.get_by_id(charge_id)

    if not charge:
        flash("Rent charge not found.", "danger")
    else:
        repo.delete(charge_id)
        flash("Rent charge deleted successfully!", "success")

    return redirect(url_for("rent_charges.list_charges"))
