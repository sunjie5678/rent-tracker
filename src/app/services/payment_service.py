"""Payment service for business logic."""

from datetime import date
from decimal import Decimal

from app.database import db_session
from app.models.payment_allocation import PaymentAllocation
from app.models.rent_charge import ChargeStatus, RentCharge
from app.repositories.payment_repository import PaymentRepository
from app.repositories.rent_charge_repository import RentChargeRepository


class PaymentService:
    """Service for payment-related business logic."""

    def __init__(self):
        """Initialize with repositories."""
        self._payment_repo = PaymentRepository()
        self._charge_repo = RentChargeRepository()

    def allocate_payment(
        self, payment_id: int, rent_charge_id: int, amount: float
    ) -> PaymentAllocation | None:
        """Allocate a payment to a rent charge.

        Args:
            payment_id: Payment ID
            rent_charge_id: Rent charge ID
            amount: Amount to allocate

        Returns:
            Created allocation or None if invalid
        """
        # Load payment with allocations to avoid lazy loading issues
        payment = self._payment_repo.get_with_allocations(payment_id)
        # Load charge with allocations
        charge = self._charge_repo.get_with_allocations(rent_charge_id)

        if not payment or not charge:
            return None

        # Check payment has remaining unallocated amount
        total_allocated = sum(a.amount for a in payment.allocations)
        remaining = payment.amount - total_allocated

        if Decimal(str(amount)) > remaining:
            raise ValueError("Allocation amount exceeds remaining payment amount")

        # Create allocation
        allocation = PaymentAllocation(
            payment_id=payment_id,
            rent_charge_id=rent_charge_id,
            amount=Decimal(str(amount)),
        )

        db_session.add(allocation)
        db_session.commit()

        # Update charge status
        self._update_charge_status(charge)

        return allocation

    def _update_charge_status(self, charge: RentCharge) -> None:
        """Update charge status based on payment state.

        Implements State pattern transitions:
        CHARGED → PAID/LATE/IN_ARREARS
        """
        total_allocated = Decimal(
            str(sum(a.amount for a in charge.payment_allocations))
        )
        today = date.today()

        if total_allocated >= charge.amount_due:
            charge.status = ChargeStatus.PAID
        elif total_allocated > 0 and today > charge.due_date:
            charge.status = ChargeStatus.LATE
        elif total_allocated == 0 and today > charge.due_date:
            charge.status = ChargeStatus.IN_ARREARS
        else:
            charge.status = ChargeStatus.CHARGED

        db_session.commit()

    def update_charge_status(self, charge: RentCharge) -> ChargeStatus:
        """Public method to update charge status.

        Args:
            charge: RentCharge to update

        Returns:
            The new status
        """
        self._update_charge_status(charge)
        return charge.status

    def get_payment_history(self, property_id: int) -> dict:
        """Get complete payment history for a property.

        Returns:
            Dict with payments, charges, and allocations
        """
        from sqlalchemy.orm import joinedload

        payments = self._payment_repo.get_by_property(property_id)
        charges = self._charge_repo.get_by_property(property_id)

        return {
            "payments": payments,
            "charges": charges,
            "total_payments": sum(p.amount for p in payments),
            "total_charges": sum(c.amount_due for c in charges),
        }

    def get_outstanding_charges(self, property_id: int) -> list[RentCharge]:
        """Get outstanding (unpaid) charges for a property."""
        return self._charge_repo.get_outstanding_by_property(property_id)

    def get_payment_balance(self, payment_id: int) -> Decimal:
        """Get remaining unallocated amount for a payment.

        Args:
            payment_id: Payment ID

        Returns:
            Unallocated amount (Decimal)
        """
        payment = self._payment_repo.get_with_allocations(payment_id)
        if not payment:
            return Decimal("0")

        total_allocated = sum(a.amount for a in payment.allocations)
        return payment.amount - total_allocated

    def auto_allocate_payment(self, payment_id: int) -> list[PaymentAllocation]:
        """Auto-allocate payment to outstanding charges (oldest first by due_date).

        Args:
            payment_id: Payment ID

        Returns:
            List of created allocations
        """
        payment = self._payment_repo.get_with_allocations(payment_id)
        if not payment:
            return []

        remaining = self.get_payment_balance(payment_id)
        if remaining <= 0:
            return []

        # Get outstanding charges ordered by due_date (oldest first)
        charges = self._charge_repo.get_outstanding_by_property(payment.property_id)

        allocations = []
        for charge in charges:
            if remaining <= 0:
                break

            # Calculate outstanding amount on this charge
            allocated = sum(a.amount for a in charge.payment_allocations)
            charge_remaining = charge.amount_due - allocated

            if charge_remaining <= 0:
                continue

            # Allocate as much as possible (up to the charge remaining)
            alloc_amount = min(remaining, charge_remaining)

            allocation = self.allocate_payment(
                payment_id, charge.id, float(alloc_amount)
            )
            if allocation:
                allocations.append(allocation)
                remaining -= alloc_amount

        return allocations

    def delete_allocation(self, allocation_id: int) -> bool:
        """Delete a payment allocation and update charge status.

        Args:
            allocation_id: Allocation ID to delete

        Returns:
            True if deleted, False if not found
        """
        from app.database import db_session

        allocation = db_session.get(PaymentAllocation, allocation_id)
        if not allocation:
            return False

        charge = allocation.rent_charge
        db_session.delete(allocation)
        db_session.commit()

        # Update charge status after removal
        self._update_charge_status(charge)

        return True
