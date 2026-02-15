"""Payment allocation - links payments to rent charges for arrears calculation."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PaymentAllocation(Base):
    """Allocates a payment (or portion) to a rent charge. Supports partial payments."""

    __tablename__ = "payment_allocations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id", ondelete="CASCADE"), nullable=False
    )
    rent_charge_id: Mapped[int] = mapped_column(
        ForeignKey("rent_charges.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    payment: Mapped["Payment"] = relationship("Payment", back_populates="allocations")
    rent_charge: Mapped["RentCharge"] = relationship(
        "RentCharge", back_populates="payment_allocations"
    )
