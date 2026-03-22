"""Rent charge State pattern: behavior per status + transition resolver."""

from functools import lru_cache

from app.models.rent_charge import ChargeStatus

from app.domain.charge_states.behaviors import ChargeStateBehavior, get_behavior
from app.domain.charge_states.transitions import ChargeStatusResolver

__all__ = [
    "ChargeStateBehavior",
    "ChargeStatusResolver",
    "get_behavior",
    "statuses_in_arrears_report",
    "statuses_in_total_arrears_money",
    "statuses_outstanding_charges",
    "statuses_overdue_due_passed",
    "statuses_upcoming_dues",
]


def _statuses_where(method: str) -> tuple[ChargeStatus, ...]:
    return tuple(
        s
        for s in ChargeStatus
        if getattr(get_behavior(s), method)()
    )


@lru_cache
def statuses_in_arrears_report() -> tuple[ChargeStatus, ...]:
    return _statuses_where("includes_in_arrears_report")


@lru_cache
def statuses_in_total_arrears_money() -> tuple[ChargeStatus, ...]:
    return _statuses_where("counts_in_total_arrears_money")


@lru_cache
def statuses_outstanding_charges() -> tuple[ChargeStatus, ...]:
    return _statuses_where("included_in_outstanding_charges")


@lru_cache
def statuses_overdue_due_passed() -> tuple[ChargeStatus, ...]:
    return _statuses_where("included_in_overdue_due_passed_query")


@lru_cache
def statuses_upcoming_dues() -> tuple[ChargeStatus, ...]:
    return _statuses_where("eligible_for_upcoming_dues")
