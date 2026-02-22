"""Payment factory for creating Payment objects."""

from datetime import date

from app.models.payment import Payment
from app.repositories.payment_repository import PaymentRepository
from app.repositories.rent_charge_repository import RentChargeRepository
from app.services.payment_service import PaymentService


class PaymentFactory:
    """Factory for creating Payment objects with allocation logic."""

    def __init__(
        self,
        payment_repository: PaymentRepository | None = None,
        charge_repository: RentChargeRepository | None = None,
    ):
        """Initialize factory with optional repositories."""
        self._payment_repo = payment_repository or PaymentRepository()
        self._charge_repo = charge_repository or RentChargeRepository()

    def create(
        self,
        property_id: int,
        amount: float,
        payment_date: date | None = None,
        notes: str | None = None,
    ) -> Payment:
        """Create a new Payment with validation.

        Args:
            property_id: ID of the property receiving payment
            amount: Payment amount
            payment_date: Date of payment (defaults to today)
            notes: Optional payment notes

        Returns:
            Created Payment instance

        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not property_id:
            raise ValueError("Property ID is required")

        amount = float(amount)
        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        if payment_date is None:
            payment_date = date.today()

        # Create payment
        data = {
            "property_id": property_id,
            "amount": amount,
            "payment_date": payment_date,
            "notes": notes.strip() if notes else None,
        }

        return self._payment_repo.create(data)

    def create_and_allocate(
        self,
        property_id: int,
        amount: float,
        charge_id: int | None = None,
        payment_date: date | None = None,
        notes: str | None = None,
    ) -> tuple[Payment, list]:
        """Create payment and optionally allocate to a charge.

        Args:
            property_id: ID of the property receiving payment
            amount: Payment amount
            charge_id: Optional charge ID to allocate to
            payment_date: Date of payment (defaults to today)
            notes: Optional payment notes

        Returns:
            Tuple of (Payment, allocations list)
        """
        payment = self.create(property_id, amount, payment_date, notes)

        allocations = []
        if charge_id:
            service = PaymentService()
            allocation = service.allocate_payment(payment.id, charge_id, amount)
            if allocation:
                allocations.append(allocation)

        return payment, allocations

    def create_unallocated(
        self,
        property_id: int,
        amount: float,
        payment_date: date | None = None,
        notes: str | None = None,
    ) -> Payment:
        """Create payment without any allocation.

        Args:
            property_id: ID of the property receiving payment
            amount: Payment amount
            payment_date: Date of payment (defaults to today)
            notes: Optional payment notes

        Returns:
            Created Payment instance
        """
        return self.create(property_id, amount, payment_date, notes)
