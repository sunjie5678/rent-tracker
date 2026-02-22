"""WTForms for rent charge management."""

from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class RentChargeForm(FlaskForm):
    """Form for creating rent charges manually (for backfilling data)."""

    property_id = SelectField(
        "Property",
        coerce=int,
        validators=[DataRequired(message="Property is required")],
    )

    period_start = DateField(
        "Period Start",
        validators=[DataRequired(message="Period start date is required")],
        format="%Y-%m-%d",
    )

    period_end = DateField(
        "Period End",
        validators=[DataRequired(message="Period end date is required")],
        format="%Y-%m-%d",
    )

    due_date = DateField(
        "Due Date",
        validators=[DataRequired(message="Due date is required")],
        format="%Y-%m-%d",
    )

    amount_due = DecimalField(
        "Amount Due ($)",
        validators=[
            DataRequired(message="Amount is required"),
            NumberRange(min=0.01, message="Amount must be positive"),
        ],
        render_kw={"placeholder": "1000.00", "step": "0.01"},
    )

    submit = SubmitField("Create Rent Charge")

    def __init__(self, *args, **kwargs):
        """Initialize form with property choices."""
        super().__init__(*args, **kwargs)
        from app.repositories.property_repository import PropertyRepository

        repo = PropertyRepository()
        properties = repo.get_all()
        self.property_id.choices = [(0, "Select a property")] + [
            (p.id, f"{p.address}, {p.city}") for p in properties
        ]


class RentChargeFilterForm(FlaskForm):
    """Form for filtering rent charges."""

    property_id = SelectField("Filter by Property", coerce=int)
    status = SelectField(
        "Status",
        choices=[
            ("", "All Statuses"),
            ("charged", "Charged"),
            ("paid", "Paid"),
            ("late", "Late"),
            ("in_arrears", "In Arrears"),
        ],
    )
    submit = SubmitField("Filter")

    def __init__(self, *args, **kwargs):
        """Initialize form with property choices."""
        super().__init__(*args, **kwargs)
        from app.repositories.property_repository import PropertyRepository

        repo = PropertyRepository()
        properties = repo.get_all()
        self.property_id.choices = [(0, "All Properties")] + [
            (p.id, f"{p.address}, {p.city}") for p in properties
        ]
