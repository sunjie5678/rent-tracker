"""WTForms for payment allocation management."""

from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class AllocationForm(FlaskForm):
    """Form for creating payment allocations."""

    rent_charge_id = SelectField(
        "Rent Charge",
        validators=[DataRequired(message="Rent charge is required")],
        coerce=int,
    )

    amount = DecimalField(
        "Amount to Allocate ($)",
        validators=[
            DataRequired(message="Amount is required"),
            NumberRange(min=0.01, message="Amount must be positive"),
        ],
        render_kw={"placeholder": "0.00", "step": "0.01"},
    )

    submit = SubmitField("Allocate Payment")

    def __init__(self, property_id: int | None = None, *args, **kwargs):
        """Initialize form with charge choices for a property.

        Args:
            property_id: Filter charges by this property
        """
        super().__init__(*args, **kwargs)
        if property_id:
            from app.repositories.rent_charge_repository import RentChargeRepository

            repo = RentChargeRepository()
            charges = repo.get_outstanding_by_property(property_id)
            self.rent_charge_id.choices = [
                (
                    c.id,
                    f"{c.period_start.strftime('%b %d')} - "
                    f"{c.period_end.strftime('%b %d, %Y')} "
                    f"(${c.amount_due:,.2f} due {c.due_date.strftime('%b %d')})",
                )
                for c in charges
            ]
        else:
            self.rent_charge_id.choices = []


class AutoAllocationForm(FlaskForm):
    """Form for auto-allocating payment to outstanding charges."""

    submit = SubmitField("Auto-Allocate to Outstanding Charges")
