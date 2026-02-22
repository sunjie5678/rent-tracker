"""Property routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.factories.property_factory import PropertyFactory
from app.forms.property_forms import PropertyEditForm, PropertyForm
from app.repositories.property_repository import PropertyRepository
from app.services.report_service import ReportService

bp = Blueprint("properties", __name__)


@bp.route("/")
def list_properties():
    """List all properties."""
    repo = PropertyRepository()
    properties_with_count = repo.get_with_tenant_count()

    return render_template(
        "properties/list.html",
        properties=properties_with_count,
    )


@bp.route("/new", methods=["GET", "POST"])
def create():
    """Create new property."""
    form = PropertyForm()

    if form.validate_on_submit():
        try:
            factory = PropertyFactory()
            factory.create(
                address=form.address.data,
                city=form.city.data,
                postal_code=form.postal_code.data,
                monthly_rent=float(form.monthly_rent.data),
            )
            flash("Property created successfully!", "success")
            return redirect(url_for("properties.list_properties"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template(
        "properties/create.html",
        form=form,
    )


@bp.route("/<int:property_id>")
def detail(property_id: int):
    """Property detail page."""
    report_service = ReportService()
    report = report_service.get_property_report(property_id)

    if not report:
        flash("Property not found.", "danger")
        return redirect(url_for("properties.list_properties"))

    return render_template(
        "properties/detail.html",
        property=report["property"],
        report=report,
    )


@bp.route("/<int:property_id>/edit", methods=["GET", "POST"])
def edit(property_id: int):
    """Edit property."""
    repo = PropertyRepository()
    property_obj = repo.get_by_id(property_id)

    if not property_obj:
        flash("Property not found.", "danger")
        return redirect(url_for("properties.list_properties"))

    form = PropertyEditForm(obj=property_obj)

    if form.validate_on_submit():
        data = {
            "address": form.address.data,
            "city": form.city.data,
            "postal_code": form.postal_code.data,
            "monthly_rent": float(form.monthly_rent.data),
            "is_active": form.is_active.data,
        }
        repo.update(property_id, data)
        flash("Property updated successfully!", "success")
        return redirect(url_for("properties.detail", property_id=property_id))

    return render_template(
        "properties/edit.html",
        form=form,
        property=property_obj,
    )


@bp.route("/<int:property_id>/delete", methods=["POST"])
def delete(property_id: int):
    """Delete property."""
    repo = PropertyRepository()
    property_obj = repo.get_by_id(property_id)

    if not property_obj:
        flash("Property not found.", "danger")
    else:
        repo.delete(property_id)
        flash("Property deleted successfully!", "success")

    return redirect(url_for("properties.list_properties"))
