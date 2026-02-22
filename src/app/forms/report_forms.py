"""WTForms for reports."""

from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField
from wtforms.validators import DataRequired


class DateRangeForm(FlaskForm):
    """Form for date range selection."""

    start_date = DateField(
        "Start Date",
        validators=[DataRequired()],
        format="%Y-%m-%d",
        default=date.today().replace(day=1),
    )

    end_date = DateField(
        "End Date",
        validators=[DataRequired()],
        format="%Y-%m-%d",
        default=date.today(),
    )

    submit = SubmitField("Generate Report")


class PropertyReportForm(FlaskForm):
    """Form for selecting property report."""

    property_id = SelectField(
        "Property",
        validators=[DataRequired()],
        coerce=int,
    )

    submit = SubmitField("View Report")

    def __init__(self, *args, **kwargs):
        """Initialize form with property choices."""
        super().__init__(*args, **kwargs)
        from app.repositories.property_repository import PropertyRepository

        repo = PropertyRepository()
        properties = repo.get_all()
        self.property_id.choices = [
            (p.id, f"{p.address}, {p.city}") for p in properties
        ]
