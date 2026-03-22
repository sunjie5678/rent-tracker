"""Compute next ChargeStatus from ledger facts (single place for transition rules)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.models.rent_charge import ChargeStatus


class ChargeStatusResolver:
    """Derives the correct status after payments — rules live here, not scattered."""

    @staticmethod
    def resolve_from_ledger(
        total_allocated: Decimal,
        amount_due: Decimal,
        due_date: date,
        today: date | None = None,
    ) -> ChargeStatus:
        if today is None:
            today = date.today()

        if total_allocated >= amount_due:
            return ChargeStatus.PAID
        if total_allocated > Decimal("0") and today > due_date:
            return ChargeStatus.LATE
        if total_allocated == Decimal("0") and today > due_date:
            return ChargeStatus.IN_ARREARS
        return ChargeStatus.CHARGED
