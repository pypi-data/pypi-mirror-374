"""Configuration and constant values for the Bikram Sambat date utilities.
"""
from __future__ import annotations
import datetime as _dt
from .bs_lookup import BS_YEARS  # local copy of calendar data

# Core Conversion Anchors
BASE_AD: _dt.date = _dt.date(2018, 4, 14)  # 2018-04-14 AD
BASE_BS: tuple[int, int, int] = (2075, 1, 1)  # 2075-01-01 BS

# Calendar Ranges
MIN_BS_YEAR: int = min(BS_YEARS.keys())
MAX_BS_YEAR: int = max(BS_YEARS.keys())

# Localized Names
BS_MONTH_NAMES = [
	"बैशाख", "जेठ", "असार", "साउन", "भदौ", "आश्विन",
	"कार्तिक", "मंसिर", "पौष", "माघ", "फाल्गुन", "चैत्र"
]

# Weekday mapping: Sunday=0 ... Saturday=6
BS_WEEKDAY_NAMES = [
	"आइतबार", "सोमबार", "मंगलबार", "बुधबार", "बिहिबार", "शुक्रबार", "शनिबार"
]

__all__ = [
	"BASE_AD",
	"BASE_BS",
	"MIN_BS_YEAR",
	"MAX_BS_YEAR",
	"BS_MONTH_NAMES",
	"BS_WEEKDAY_NAMES",
	"BS_YEARS",
]
