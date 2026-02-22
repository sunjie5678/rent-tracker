"""WTForms for tenant management."""

from flask_wtf import FlaskForm
from wtforms import DateField, EmailField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class TenantForm(FlaskForm):
    """Form for creating/editing tenants."""

    property_id = SelectField(
        "Property",
        validators=[DataRequired(message="Property is required")],
        coerce=int,
    )

    name = StringField(
        "Tenant Name",
        validators=[
            DataRequired(message="Name is required"),
            Length(max=255, message="Name must be less than 255 characters"),
        ],
        render_kw={"placeholder": "John Doe"},
    )

    email = EmailField(
        "Email",
        validators=[
            Optional(),
            Email(message="Invalid email address"),
            Length(max=255, message="Email must be less than 255 characters"),
        ],
        render_kw={"placeholder": "tenant@example.com"},
    )

    phone = StringField(
        "Phone",
        validators=[
            Optional(),
            Length(max=50, message="Phone must be less than 50 characters"),
        ],
        render_kw={"placeholder": "+1 (555) 123-4567"},
    )

    move_in_date = DateField(
        "Move-in Date",
        validators=[DataRequired(message="Move-in date is required")],
        format="%Y-%m-%d",
    )

    move_out_date = DateField(
        "Move-out Date",
        validators=[Optional()],
        format="%Y-%m-%d",
    )

    submit = SubmitField("Save Tenant")

    def __init__(self, *args, **kwargs):
        """Initialize form with property choices."""
        super().__init__(*args, **kwargs)
        from app.repositories.property_repository import PropertyRepository

        repo = PropertyRepository()
        properties = repo.get_active()
        self.property_id.choices = [
            (p.id, f"{p.address}, {p.city}") for p in properties
        ]


class TenantEditForm(TenantForm):
    """Form for editing existing tenants."""

    submit = SubmitField("Update Tenant")


class TenantFilterForm(FlaskForm):
    """Form for filtering tenants."""

    property_id = SelectField("Filter by Property", coerce=int)
    submit = SubmitField("Filter")

    def __init__(self, *args, **kwargs):
        """Initialize form with property choices including 'All'."""
        super().__init__(*args, **kwargs)
        from app.repositories.property_repository import PropertyRepository

        repo = PropertyRepository()
        properties = repo.get_all()
        self.property_id.choices = [(0, "All Properties")] + [
            (p.id, f"{p.address}, {p.city}") for p in properties
        ]
