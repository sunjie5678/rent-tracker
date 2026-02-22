"""Payment repository."""

from datetime import date

from sqlalchemy import func

from app.models.payment import Payment
from app.repositories.base_repository import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Repository for Payment operations."""

    def __init__(self, session=None):
        """Initialize with Payment model."""
        super().__init__(Payment, session)

    def get_by_property(self, property_id: int, limit: int | None = None) -> list[Payment]:
        """Get payments for a property, ordered by date."""
        query = (
            self._session.query(Payment)
            .filter(Payment.property_id == property_id)
            .order_by(Payment.payment_date.desc())
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_by_date_range(
        self, start_date: date, end_date: date, property_id: int | None = None
    ) -> list[Payment]:
        """Get payments within a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            property_id: Optional property filter
        """
        query = self._session.query(Payment).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date,
        )
        if property_id:
            query = query.filter(Payment.property_id == property_id)
        return query.order_by(Payment.payment_date.desc()).all()

    def get_total_by_property(self, property_id: int) -> float:
        """Get total payments received for a property."""
        result = (
            self._session.query(func.sum(Payment.amount))
            .filter(Payment.property_id == property_id)
            .scalar()
        )
        return float(result) if result else 0.0

    def get_recent(self, limit: int = 5) -> list[Payment]:
        """Get recent payments across all properties."""
        return (
            self._session.query(Payment)
            .order_by(Payment.payment_date.desc())
            .limit(limit)
            .all()
        )

    def get_with_allocations(self, payment_id: int) -> Payment | None:
        """Get payment with its allocations loaded."""
        from sqlalchemy.orm import joinedload

        return (
            self._session.query(Payment)
            .options(joinedload(Payment.allocations))
            .filter(Payment.id == payment_id)
            .first()
        )
