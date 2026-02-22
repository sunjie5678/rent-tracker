"""Payment routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.factories.payment_factory import PaymentFactory
from app.forms.payment_forms import PaymentFilterForm, PaymentForm
from app.repositories.payment_repository import PaymentRepository
from app.repositories.property_repository import PropertyRepository
from app.services.payment_service import PaymentService

bp = Blueprint("payments", __name__)


@bp.route("/")
def list_payments():
    """List all payments."""
    repo = PaymentRepository()
    filter_form = PaymentFilterForm(request.args)

    property_id = request.args.get("property_id", type=int)

    if property_id:
        payments = repo.get_by_property(property_id)
    else:
        payments = repo.get_all()

    # Get property names for display
    prop_repo = PropertyRepository()
    properties = {p.id: p for p in prop_repo.get_all()}

    return render_template(
        "payments/list.html",
        payments=payments,
        properties=properties,
        filter_form=filter_form,
    )


@bp.route("/new", methods=["GET", "POST"])
def create():
    """Create new payment."""
    form = PaymentForm()

    if form.validate_on_submit():
        try:
            factory = PaymentFactory()
            payment = factory.create(
                property_id=form.property_id.data,
                amount=float(form.amount.data),
                payment_date=form.payment_date.data,
                notes=form.notes.data,
            )
            flash(
                "Payment recorded successfully! "
                f"<a href='{url_for('allocations.allocate', payment_id=payment.id)}'>"
                "Allocate now</a>",
                "success",
            )
            return redirect(url_for("payments.detail", payment_id=payment.id))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template(
        "payments/create.html",
        form=form,
    )


@bp.route("/<int:payment_id>")
def detail(payment_id: int):
    """Payment detail page."""
    repo = PaymentRepository()
    payment = repo.get_with_allocations(payment_id)

    if not payment:
        flash("Payment not found.", "danger")
        return redirect(url_for("payments.list_payments"))

    # Calculate remaining balance
    service = PaymentService()
    balance = service.get_payment_balance(payment_id)

    return render_template(
        "payments/detail.html",
        payment=payment,
        balance=balance,
    )


@bp.route("/<int:payment_id>/delete", methods=["POST"])
def delete(payment_id: int):
    """Delete payment."""
    repo = PaymentRepository()
    payment = repo.get_by_id(payment_id)

    if not payment:
        flash("Payment not found.", "danger")
    else:
        repo.delete(payment_id)
        flash("Payment deleted successfully!", "success")

    return redirect(url_for("payments.list_payments"))
