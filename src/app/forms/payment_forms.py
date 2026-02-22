"""WTForms for payment management."""

from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class PaymentForm(FlaskForm):
    """Form for recording payments."""

    property_id = SelectField(
        "Property",
        validators=[DataRequired(message="Property is required")],
        coerce=int,
    )

    amount = DecimalField(
        "Amount ($)",
        validators=[
            DataRequired(message="Amount is required"),
            NumberRange(min=0.01, message="Amount must be positive"),
        ],
        render_kw={"placeholder": "1000.00", "step": "0.01"},
    )

    payment_date = DateField(
        "Payment Date",
        validators=[DataRequired(message="Payment date is required")],
        format="%Y-%m-%d",
    )

    notes = TextAreaField(
        "Notes",
        validators=[
            Optional(),
            Length(max=500, message="Notes must be less than 500 characters"),
        ],
        render_kw={
            "placeholder": "Optional payment notes...",
            "rows": 3,
        },
    )

    submit = SubmitField("Record Payment")

    def __init__(self, *args, **kwargs):
        """Initialize form with property choices."""
        super().__init__(*args, **kwargs)
        from app.repositories.property_repository import PropertyRepository

        repo = PropertyRepository()
        properties = repo.get_active()
        self.property_id.choices = [
            (p.id, f"{p.address}, {p.city}") for p in properties
        ]


class PaymentFilterForm(FlaskForm):
    """Form for filtering payments."""

    property_id = SelectField("Filter by Property", coerce=int)
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
