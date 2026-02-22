"""WTForms for property management."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, DecimalField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class PropertyForm(FlaskForm):
    """Form for creating/editing properties."""

    address = StringField(
        "Address",
        validators=[
            DataRequired(message="Address is required"),
            Length(max=255, message="Address must be less than 255 characters"),
        ],
        render_kw={"placeholder": "123 Main Street"},
    )

    city = StringField(
        "City",
        validators=[
            DataRequired(message="City is required"),
            Length(max=100, message="City must be less than 100 characters"),
        ],
        render_kw={"placeholder": "City name"},
    )

    postal_code = StringField(
        "Postal Code",
        validators=[
            DataRequired(message="Postal code is required"),
            Length(max=20, message="Postal code must be less than 20 characters"),
        ],
        render_kw={"placeholder": "A1B 2C3"},
    )

    monthly_rent = DecimalField(
        "Monthly Rent ($)",
        validators=[
            DataRequired(message="Monthly rent is required"),
            NumberRange(min=0.01, message="Rent must be positive"),
        ],
        render_kw={"placeholder": "1000.00", "step": "0.01"},
    )

    is_active = BooleanField("Active Property", default=True)

    submit = SubmitField("Save Property")


class PropertyEditForm(PropertyForm):
    """Form for editing existing properties."""

    submit = SubmitField("Update Property")
