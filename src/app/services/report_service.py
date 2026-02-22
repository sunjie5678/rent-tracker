"""Report service for generating reports and summaries."""

from datetime import date, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from app.models.rent_charge import ChargeStatus
from app.repositories.payment_repository import PaymentRepository
from app.repositories.property_repository import PropertyRepository
from app.repositories.rent_charge_repository import RentChargeRepository
from app.repositories.tenant_repository import TenantRepository

if TYPE_CHECKING:
    from app.models.property import Property


class ReportService:
    """Service for generating reports."""

    def __init__(self):
        """Initialize with repositories."""
        self._property_repo = PropertyRepository()
        self._tenant_repo = TenantRepository()
        self._payment_repo = PaymentRepository()
        self._charge_repo = RentChargeRepository()

    def get_dashboard_summary(self) -> dict:
        """Get dashboard summary statistics.

        Returns:
            Dict with summary data
        """
        # Total counts
        total_properties = self._property_repo.count()
        total_tenants = self._tenant_repo.count()

        # Monthly rent expected from active properties
        properties = self._property_repo.get_all()
        monthly_rent_expected = sum(
            p.monthly_rent for p in properties if p.is_active
        )

        # Arrears
        total_arrears = self._charge_repo.get_total_arrears()

        # Recent payments
        recent_payments = self._payment_repo.get_recent(limit=5)

        # Upcoming dues
        upcoming_charges = self._charge_repo.get_upcoming(days=7)

        # Recent rent charges (past 30 days)
        recent_charges = self._charge_repo.get_recent(days=30)

        # Charge counts by status
        charges_by_status = {
            "charged": len(self._charge_repo.get_by_status(ChargeStatus.CHARGED)),
            "paid": len(self._charge_repo.get_by_status(ChargeStatus.PAID)),
            "late": len(self._charge_repo.get_by_status(ChargeStatus.LATE)),
            "in_arrears": len(
                self._charge_repo.get_by_status(ChargeStatus.IN_ARREARS)
            ),
        }

        return {
            "total_properties": total_properties,
            "total_tenants": total_tenants,
            "monthly_rent_expected": monthly_rent_expected,
            "total_arrears": total_arrears,
            "recent_payments": recent_payments,
            "upcoming_charges": upcoming_charges,
            "recent_charges": recent_charges,
            "charges_by_status": charges_by_status,
        }

    def get_property_report(self, property_id: int) -> dict | None:
        """Get detailed report for a property.

        Args:
            property_id: Property ID

        Returns:
            Report data or None if property not found
        """
        property_obj = self._property_repo.get_by_id(property_id)
        if not property_obj:
            return None

        # Tenants
        tenants = self._tenant_repo.get_by_property(property_id)
        current_tenants = [t for t in tenants if t.move_out_date is None]

        # Payments
        payments = self._payment_repo.get_by_property(property_id)
        total_payments = sum(p.amount for p in payments)

        # Rent charges
        charges = self._charge_repo.get_by_property(property_id)
        total_charges = sum(c.amount_due for c in charges)

        # Balance
        balance = total_charges - total_payments

        return {
            "property": property_obj,
            "tenants": tenants,
            "current_tenants": current_tenants,
            "payments": payments,
            "charges": charges,
            "total_payments": total_payments,
            "total_charges": total_charges,
            "balance": balance,
        }

    def get_arrears_report(self) -> list[dict]:
        """Get arrears report with tenant information.

        Returns:
            List of dicts with arrears details
        """
        from collections import defaultdict

        # Get late and in-arrears charges
        late_charges = self._charge_repo.get_by_status(ChargeStatus.LATE)
        arrears_charges = self._charge_repo.get_by_status(
            ChargeStatus.IN_ARREARS
        )

        all_overdue = late_charges + arrears_charges

        # Group by tenant
        by_tenant = defaultdict(list)
        for charge in all_overdue:
            tenants = [
                t for t in charge.property.tenants if t.move_out_date is None
            ]
            for tenant in tenants:
                by_tenant[tenant].append(charge)

        # Build report
        report = []
        for tenant, charges in by_tenant.items():
            total = sum(c.amount_due for c in charges)
            oldest_due = min(c.due_date for c in charges)
            days_overdue = (date.today() - oldest_due).days

            report.append(
                {
                    "tenant": tenant,
                    "property": tenant.property,
                    "charges": charges,
                    "total_outstanding": total,
                    "oldest_due": oldest_due,
                    "days_overdue": days_overdue,
                    "has_email": bool(tenant.email),
                }
            )

        # Sort by days overdue (descending)
        report.sort(key=lambda x: x["days_overdue"], reverse=True)

        return report

    def get_payment_timeline(self, property_id: int, months: int = 12) -> list[dict]:
        """Get payment timeline for a property.

        Args:
            property_id: Property ID
            months: Number of months to include

        Returns:
            List of monthly payment data
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=30 * months)

        payments = self._payment_repo.get_by_date_range(start_date, end_date)
        payments = [p for p in payments if p.property_id == property_id]

        # Group by month
        by_month = {}
        for p in payments:
            month_key = p.payment_date.strftime("%Y-%m")
            if month_key not in by_month:
                by_month[month_key] = []
            by_month[month_key].append(p)

        # Build timeline
        timeline = []
        current = start_date
        while current <= end_date:
            month_key = current.strftime("%Y-%m")
            month_payments = by_month.get(month_key, [])

            timeline.append(
                {
                    "month": current.strftime("%B %Y"),
                    "payment_count": len(month_payments),
                    "total": sum(p.amount for p in month_payments),
                }
            )

            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return timeline

    def get_financial_summary(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> dict:
        """Get financial summary for a date range.

        Args:
            start_date: Start date (defaults to start of current year)
            end_date: End date (defaults to today)

        Returns:
            Financial summary dict
        """
        if start_date is None:
            start_date = date(date.today().year, 1, 1)
        if end_date is None:
            end_date = date.today()

        payments = self._payment_repo.get_by_date_range(start_date, end_date)
        total_received = sum(p.amount for p in payments)

        charges = self._charge_repo.get_by_date_range(
            start_date, end_date
        )
        total_charged = sum(c.amount_due for c in charges)

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_received": total_received,
            "total_charged": total_charged,
            "outstanding": total_charged - total_received,
            "payment_count": len(payments),
            "charge_count": len(charges),
        }

    def get_occupancy_report(self) -> list[dict]:
        """Get occupancy report for all properties.

        Returns:
            List of property occupancy data
        """
        properties = self._property_repo.get_all()
        report = []

        for prop in properties:
            current_tenants = [
                t for t in prop.tenants if t.move_out_date is None
            ]
            # Assume single occupancy for simplicity
            is_occupied = len(current_tenants) > 0

            report.append(
                {
                    "property": prop,
                    "is_occupied": is_occupied,
                    "tenant_count": len(current_tenants),
                    "tenants": current_tenants,
                }
            )

        return report

    def get_tenant_payment_history(self, tenant_id: int) -> dict | None:
        """Get payment history for a tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            Payment history dict or None
        """
        from app.database import db_session

        tenant = self._tenant_repo.get_by_id(tenant_id)
        if not tenant:
            return None

        property_id = tenant.property_id
        charges = self._charge_repo.get_by_property(property_id)

        # Get allocations for this property
        from app.models.payment_allocation import PaymentAllocation

        allocations = (
            db_session.query(PaymentAllocation)
            .join(PaymentAllocation.payment)
            .filter(PaymentAllocation.payment.has(property_id=property_id))
            .all()
        )

        # Calculate total paid
        total_paid = sum(a.amount for a in allocations)

        return {
            "tenant": tenant,
            "property": tenant.property,
            "charges": charges,
            "allocations": allocations,
            "total_paid": total_paid,
            "residency_period": {
                "move_in": tenant.move_in_date,
                "move_out": tenant.move_out_date,
            },
        }
