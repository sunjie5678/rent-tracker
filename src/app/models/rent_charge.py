"""Rent charge model with payment state (Charged, Paid, Late, In Arrears)."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLEnum, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ChargeStatus(str, Enum):
    """Rental payment state - supports State pattern for status transitions."""

    CHARGED = "charged"      # Rent charged, not yet due
    PAID = "paid"            # Fully paid
    LATE = "late"            # Past due, partially paid
    IN_ARREARS = "in_arrears"  # Past due, unpaid or underpaid


class RentCharge(Base):
    """Rent charge for a property for a given period. Tracks state: Charged, Paid, Late, In Arrears."""

    __tablename__ = "rent_charges"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), nullable=False
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    amount_due: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ChargeStatus] = mapped_column(
        SQLEnum(ChargeStatus), default=ChargeStatus.CHARGED, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    property: Mapped["Property"] = relationship("Property", back_populates="rent_charges")
    payment_allocations: Mapped[list["PaymentAllocation"]] = relationship(
        "PaymentAllocation",
        back_populates="rent_charge",
        cascade="all, delete-orphan",
    )
