"""Bikram Sambat (Nepali) date & datetime utilities.

Renamed distribution: bsdatetime (formerly bikram-sambat).
This module preserves the public API from the former bikram_sambat package.
"""

__version__ = "1.1.0"

from .config import (
    BASE_AD,
    BASE_BS,
    MIN_BS_YEAR,
    MAX_BS_YEAR,
    BS_MONTH_NAMES,
    BS_WEEKDAY_NAMES,
)
from . import utils
from .conversion import ad_to_bs, bs_to_ad
from .validation import is_valid_bs_date, get_bs_month_days
from .formatting import (
    format_bs_date,
    parse_bs_date,
    format_bs_datetime,
    parse_bs_datetime,
)

__all__ = [
    "__version__",
    "BASE_AD",
    "BASE_BS",
    "MIN_BS_YEAR",
    "MAX_BS_YEAR",
    "BS_MONTH_NAMES",
    "BS_WEEKDAY_NAMES",
    "utils",
    "ad_to_bs",
    "bs_to_ad",
    "is_valid_bs_date",
    "get_bs_month_days",
    "format_bs_date",
    "parse_bs_date",
    "format_bs_datetime",
    "parse_bs_datetime",
]
