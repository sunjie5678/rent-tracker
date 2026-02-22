"""Allocation routes."""

from flask import Blueprint, flash, redirect, render_template, url_for

from app.forms.allocation_forms import AllocationForm, AutoAllocationForm
from app.repositories.payment_repository import PaymentRepository
from app.repositories.rent_charge_repository import RentChargeRepository
from app.services.payment_service import PaymentService

bp = Blueprint("allocations", __name__)


@bp.route("/<int:payment_id>/allocate", methods=["GET", "POST"])
def allocate(payment_id: int):
    """Allocate payment to rent charges."""
    payment_repo = PaymentRepository()
    payment = payment_repo.get_with_allocations(payment_id)

    if not payment:
        flash("Payment not found.", "danger")
        return redirect(url_for("payments.list_payments"))

    # Get outstanding charges for this property (ordered oldest first)
    charge_repo = RentChargeRepository()
    outstanding = charge_repo.get_outstanding_by_property(payment.property_id)

    # Calculate remaining balance
    service = PaymentService()
    balance = service.get_payment_balance(payment_id)

    form = AllocationForm(property_id=payment.property_id)
    auto_form = AutoAllocationForm()

    # Validate that there are charges to allocate to
    if not outstanding:
        flash("No outstanding charges to allocate to for this property.", "warning")
        return render_template(
            "allocations/form.html",
            payment=payment,
            outstanding=outstanding,
            balance=balance,
            form=form,
            auto_form=auto_form,
        )

    if form.validate_on_submit():
        try:
            service.allocate_payment(
                payment_id=payment_id,
                rent_charge_id=form.rent_charge_id.data,
                amount=float(form.amount.data),
            )
            flash("Payment allocated successfully!", "success")
            return redirect(url_for("payments.detail", payment_id=payment_id))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template(
        "allocations/form.html",
        payment=payment,
        outstanding=outstanding,
        balance=balance,
        form=form,
        auto_form=auto_form,
    )


@bp.route("/<int:payment_id>/auto-allocate", methods=["POST"])
def auto_allocate(payment_id: int):
    """Auto-allocate payment to outstanding charges (oldest first by due date)."""
    payment_repo = PaymentRepository()
    payment = payment_repo.get_with_allocations(payment_id)

    if not payment:
        flash("Payment not found.", "danger")
        return redirect(url_for("payments.list_payments"))

    service = PaymentService()
    allocations = service.auto_allocate_payment(payment_id)

    if allocations:
        flash(
            f"Payment auto-allocated to {len(allocations)} charge(s).", "success"
        )
    else:
        flash("No outstanding charges to allocate to.", "warning")

    return redirect(url_for("payments.detail", payment_id=payment_id))


@bp.route("/delete/<int:allocation_id>", methods=["POST"])
def delete_allocation(allocation_id: int):
    """Delete a payment allocation."""
    service = PaymentService()
    success = service.delete_allocation(allocation_id)

    if success:
        flash("Allocation removed successfully!", "success")
    else:
        flash("Allocation not found.", "danger")

    # Redirect back to payment detail (need to find payment_id from allocation)
    from app.database import db_session
    from app.models.payment_allocation import PaymentAllocation

    allocation = db_session.get(PaymentAllocation, allocation_id)
    if allocation:
        return redirect(
            url_for("payments.detail", payment_id=allocation.payment_id)
        )

    return redirect(url_for("payments.list_payments"))
