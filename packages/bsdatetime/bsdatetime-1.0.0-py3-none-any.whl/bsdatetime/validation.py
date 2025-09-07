"""Validation helpers for BS dates."""
from __future__ import annotations
from .config import BS_YEARS

__all__ = ["is_valid_bs_date", "get_bs_month_days"]

def is_valid_bs_date(year: int, month: int, day: int) -> bool:
    """Check if a BS date is valid."""
    if year not in BS_YEARS:
        return False
    if not (1 <= month <= 12):
        return False
    if not (1 <= day <= BS_YEARS[year][month - 1]):
        return False
    return True

def get_bs_month_days(year: int, month: int) -> int:
    """Get the number of days in a BS month."""
    if year in BS_YEARS and 1 <= month <= 12:
        return BS_YEARS[year][month - 1]
    raise ValueError("Invalid BS year or month")
