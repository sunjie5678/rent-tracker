"""Per-status behavior for rent charges (State pattern: polymorphic reporting & UI rules)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from app.models.rent_charge import ChargeStatus


class ChargeStateBehavior(ABC):
    """Behavior tied to a persisted ChargeStatus.

    Reporting and presentation ask the behavior object instead of branching on enums
    throughout the codebase.
    """

    status: ClassVar[ChargeStatus]

    @abstractmethod
    def includes_in_arrears_report(self) -> bool:
        """Tenant-level arrears report (late + materially overdue)."""

    @abstractmethod
    def counts_in_total_arrears_money(self) -> bool:
        """Include in dashboard sum of money 'in arrears'."""

    @abstractmethod
    def included_in_outstanding_charges(self) -> bool:
        """Not fully settled — eligible for allocation / outstanding lists."""

    @abstractmethod
    def included_in_overdue_due_passed_query(self) -> bool:
        """get_overdue: past due and not fully paid (subset of statuses)."""

    @abstractmethod
    def eligible_for_upcoming_dues(self) -> bool:
        """get_upcoming: not yet due, still 'charged' waiting for payment."""

    def table_row_class(self) -> str:
        """Bootstrap row class for table lists (empty string = default)."""
        return ""

    def badge_bootstrap_class(self) -> str:
        """Bootstrap badge class for status column."""
        return "bg-secondary"

    def badge_label(self) -> str:
        """Short label for badges."""
        return self.status.value.replace("_", " ").title()


class ChargedBehavior(ChargeStateBehavior):
    status = ChargeStatus.CHARGED

    def includes_in_arrears_report(self) -> bool:
        return False

    def counts_in_total_arrears_money(self) -> bool:
        return False

    def included_in_outstanding_charges(self) -> bool:
        return True

    def included_in_overdue_due_passed_query(self) -> bool:
        return True

    def eligible_for_upcoming_dues(self) -> bool:
        return True

    def table_row_class(self) -> str:
        return ""

    def badge_bootstrap_class(self) -> str:
        return "bg-primary"

    def badge_label(self) -> str:
        return "Charged"


class PaidBehavior(ChargeStateBehavior):
    status = ChargeStatus.PAID

    def includes_in_arrears_report(self) -> bool:
        return False

    def counts_in_total_arrears_money(self) -> bool:
        return False

    def included_in_outstanding_charges(self) -> bool:
        return False

    def included_in_overdue_due_passed_query(self) -> bool:
        return False

    def eligible_for_upcoming_dues(self) -> bool:
        return False

    def badge_bootstrap_class(self) -> str:
        return "bg-success"

    def badge_label(self) -> str:
        return "Paid"


class LateBehavior(ChargeStateBehavior):
    status = ChargeStatus.LATE

    def includes_in_arrears_report(self) -> bool:
        return True

    def counts_in_total_arrears_money(self) -> bool:
        return True

    def included_in_outstanding_charges(self) -> bool:
        return True

    def included_in_overdue_due_passed_query(self) -> bool:
        return True

    def eligible_for_upcoming_dues(self) -> bool:
        return False

    def table_row_class(self) -> str:
        return "table-warning"

    def badge_bootstrap_class(self) -> str:
        return "bg-warning"

    def badge_label(self) -> str:
        return "Late"


class InArrearsBehavior(ChargeStateBehavior):
    status = ChargeStatus.IN_ARREARS

    def includes_in_arrears_report(self) -> bool:
        return True

    def counts_in_total_arrears_money(self) -> bool:
        return True

    def included_in_outstanding_charges(self) -> bool:
        return True

    def included_in_overdue_due_passed_query(self) -> bool:
        return False

    def eligible_for_upcoming_dues(self) -> bool:
        return False

    def table_row_class(self) -> str:
        return "table-danger"

    def badge_bootstrap_class(self) -> str:
        return "bg-danger"

    def badge_label(self) -> str:
        return "In Arrears"


_BEHAVIORS: dict[ChargeStatus, ChargeStateBehavior] = {
    ChargeStatus.CHARGED: ChargedBehavior(),
    ChargeStatus.PAID: PaidBehavior(),
    ChargeStatus.LATE: LateBehavior(),
    ChargeStatus.IN_ARREARS: InArrearsBehavior(),
}


def get_behavior(status: ChargeStatus) -> ChargeStateBehavior:
    """Return the state object for a persisted status (State pattern entry point)."""
    return _BEHAVIORS[status]
