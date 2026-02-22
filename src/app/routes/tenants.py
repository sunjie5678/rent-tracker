"""Tenant routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.forms.tenant_forms import TenantEditForm, TenantFilterForm, TenantForm
from app.repositories.property_repository import PropertyRepository
from app.repositories.tenant_repository import TenantRepository

bp = Blueprint("tenants", __name__)


@bp.route("/")
def list_tenants():
    """List all tenants."""
    repo = TenantRepository()
    filter_form = TenantFilterForm(request.args)

    property_id = request.args.get("property_id", type=int)

    if property_id:
        tenants = repo.get_by_property(property_id)
    else:
        tenants = repo.get_all()

    # Get property names for display
    prop_repo = PropertyRepository()
    properties = {p.id: p for p in prop_repo.get_all()}

    return render_template(
        "tenants/list.html",
        tenants=tenants,
        properties=properties,
        filter_form=filter_form,
    )


@bp.route("/new", methods=["GET", "POST"])
def create():
    """Create new tenant."""
    form = TenantForm()

    if form.validate_on_submit():
        repo = TenantRepository()
        data = {
            "property_id": form.property_id.data,
            "name": form.name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "move_in_date": form.move_in_date.data,
            "move_out_date": form.move_out_date.data,
        }
        tenant = repo.create(data)
        flash("Tenant created successfully!", "success")
        return redirect(url_for("tenants.detail", tenant_id=tenant.id))

    return render_template(
        "tenants/create.html",
        form=form,
    )


@bp.route("/<int:tenant_id>")
def detail(tenant_id: int):
    """Tenant detail page."""
    repo = TenantRepository()
    tenant = repo.get_by_id(tenant_id)

    if not tenant:
        flash("Tenant not found.", "danger")
        return redirect(url_for("tenants.list_tenants"))

    # Get tenant's charges
    from app.repositories.rent_charge_repository import RentChargeRepository

    charge_repo = RentChargeRepository()
    charges = charge_repo.get_by_property(tenant.property_id)

    return render_template(
        "tenants/detail.html",
        tenant=tenant,
        charges=charges,
    )


@bp.route("/<int:tenant_id>/edit", methods=["GET", "POST"])
def edit(tenant_id: int):
    """Edit tenant."""
    repo = TenantRepository()
    tenant = repo.get_by_id(tenant_id)

    if not tenant:
        flash("Tenant not found.", "danger")
        return redirect(url_for("tenants.list_tenants"))

    form = TenantEditForm(obj=tenant)

    if form.validate_on_submit():
        data = {
            "property_id": form.property_id.data,
            "name": form.name.data,
            "email": form.email.data,
            "phone": form.phone.data,
            "move_in_date": form.move_in_date.data,
            "move_out_date": form.move_out_date.data,
        }
        repo.update(tenant_id, data)
        flash("Tenant updated successfully!", "success")
        return redirect(url_for("tenants.detail", tenant_id=tenant_id))

    return render_template(
        "tenants/edit.html",
        form=form,
        tenant=tenant,
    )


@bp.route("/<int:tenant_id>/delete", methods=["POST"])
def delete(tenant_id: int):
    """Delete tenant."""
    repo = TenantRepository()
    tenant = repo.get_by_id(tenant_id)

    if not tenant:
        flash("Tenant not found.", "danger")
    else:
        repo.delete(tenant_id)
        flash("Tenant deleted successfully!", "success")

    return redirect(url_for("tenants.list_tenants"))
