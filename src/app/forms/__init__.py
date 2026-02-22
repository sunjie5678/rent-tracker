"""WTForms for the application."""

from app.forms.allocation_forms import AllocationForm, AutoAllocationForm
from app.forms.payment_forms import PaymentFilterForm, PaymentForm
from app.forms.property_forms import PropertyEditForm, PropertyForm
from app.forms.rent_charge_forms import RentChargeFilterForm, RentChargeForm
from app.forms.report_forms import DateRangeForm, PropertyReportForm
from app.forms.tenant_forms import TenantEditForm, TenantFilterForm, TenantForm

__all__ = [
    "AllocationForm",
    "AutoAllocationForm",
    "DateRangeForm",
    "PaymentFilterForm",
    "PaymentForm",
    "PropertyEditForm",
    "PropertyForm",
    "PropertyReportForm",
    "RentChargeFilterForm",
    "RentChargeForm",
    "TenantEditForm",
    "TenantFilterForm",
    "TenantForm",
]
