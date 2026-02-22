"""Rent charge repository."""

from datetime import date

from sqlalchemy import func

from app.models.rent_charge import ChargeStatus, RentCharge
from app.repositories.base_repository import BaseRepository


class RentChargeRepository(BaseRepository[RentCharge]):
    """Repository for RentCharge operations."""

    def __init__(self, session=None):
        """Initialize with RentCharge model."""
        super().__init__(RentCharge, session)

    def get_by_property(self, property_id: int) -> list[RentCharge]:
        """Get all rent charges for a property."""
        return (
            self._session.query(RentCharge)
            .filter(RentCharge.property_id == property_id)
            .order_by(RentCharge.due_date.desc())
            .all()
        )

    def get_by_status(self, status: ChargeStatus) -> list[RentCharge]:
        """Get rent charges by status."""
        return (
            self._session.query(RentCharge)
            .filter(RentCharge.status == status)
            .order_by(RentCharge.due_date)
            .all()
        )

    def get_overdue(self, as_of_date: date | None = None) -> list[RentCharge]:
        """Get overdue charges (due date passed, not fully paid).

        Args:
            as_of_date: Date to check against (defaults to today)
        """
        if as_of_date is None:
            as_of_date = date.today()

        return (
            self._session.query(RentCharge)
            .filter(
                RentCharge.due_date < as_of_date,
                RentCharge.status.in_([ChargeStatus.CHARGED, ChargeStatus.LATE]),
            )
            .order_by(RentCharge.due_date)
            .all()
        )

    def get_upcoming(self, days: int = 7) -> list[RentCharge]:
        """Get charges due within the next N days."""
        today = date.today()
        future = date.fromordinal(today.toordinal() + days)

        return (
            self._session.query(RentCharge)
            .filter(
                RentCharge.due_date >= today,
                RentCharge.due_date <= future,
                RentCharge.status == ChargeStatus.CHARGED,
            )
            .order_by(RentCharge.due_date)
            .all()
        )

    def get_outstanding_by_property(self, property_id: int) -> list[RentCharge]:
        """Get outstanding (unpaid) charges for a property, ordered by due_date (oldest first)."""
        return (
            self._session.query(RentCharge)
            .filter(
                RentCharge.property_id == property_id,
                RentCharge.status.in_([ChargeStatus.CHARGED, ChargeStatus.LATE, ChargeStatus.IN_ARREARS]),
            )
            .order_by(RentCharge.due_date.asc())
            .all()
        )

    def get_total_arrears(self) -> float:
        """Get total amount in arrears across all properties."""
        from app.models.payment_allocation import PaymentAllocation

        # Subquery for allocated amounts
        allocated = (
            self._session.query(
                PaymentAllocation.rent_charge_id.label("charge_id"),
                func.sum(PaymentAllocation.amount).label("total_allocated"),
            )
            .group_by(PaymentAllocation.rent_charge_id)
            .subquery()
        )

        # Get charges in arrears with their outstanding amounts
        result = (
            self._session.query(
                func.sum(RentCharge.amount_due - func.coalesce(allocated.c.total_allocated, 0))
            )
            .outerjoin(allocated, RentCharge.id == allocated.c.charge_id)
            .filter(
                RentCharge.status.in_([ChargeStatus.LATE, ChargeStatus.IN_ARREARS]),
            )
            .scalar()
        )

        return float(result) if result else 0.0

    def get_with_allocations(self, charge_id: int) -> RentCharge | None:
        """Get rent charge with its payment allocations."""
        from sqlalchemy.orm import joinedload

        return (
            self._session.query(RentCharge)
            .options(joinedload(RentCharge.payment_allocations))
            .filter(RentCharge.id == charge_id)
            .first()
        )

    def get_by_date_range(
        self, start_date: date, end_date: date, property_id: int | None = None
    ) -> list[RentCharge]:
        """Get rent charges within a date range (by period).

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            property_id: Optional property filter
        """
        query = self._session.query(RentCharge).filter(
            RentCharge.period_start >= start_date,
            RentCharge.period_end <= end_date,
        )
        if property_id:
            query = query.filter(RentCharge.property_id == property_id)
        return query.order_by(RentCharge.due_date).all()

    def get_recent(self, days: int = 30) -> list[RentCharge]:
        """Get rent charges created within the past N days.

        Args:
            days: Number of days to look back (default 30)
        """
        today = date.today()
        past = date.fromordinal(today.toordinal() - days)

        return (
            self._session.query(RentCharge)
            .filter(RentCharge.created_at >= past)
            .order_by(RentCharge.created_at.desc())
            .all()
        )
