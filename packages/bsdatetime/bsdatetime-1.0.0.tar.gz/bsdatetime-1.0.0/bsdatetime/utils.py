"""Utility functions for Bikram Sambat date operations."""

import datetime
from .config import MIN_BS_YEAR, MAX_BS_YEAR, BS_WEEKDAY_NAMES, BS_MONTH_NAMES
from . import conversion as _conversion
from . import validation as _validation
from . import formatting as _formatting

# Public re-exports
ad_to_bs = _conversion.ad_to_bs
bs_to_ad = _conversion.bs_to_ad
is_valid_bs_date = _validation.is_valid_bs_date
get_bs_month_days = _validation.get_bs_month_days
format_bs_date = _formatting.format_bs_date
parse_bs_date = _formatting.parse_bs_date
format_bs_datetime = _formatting.format_bs_datetime
parse_bs_datetime = _formatting.parse_bs_datetime

__all__ = [
    # conversion
    "ad_to_bs", "bs_to_ad",
    # validation
    "is_valid_bs_date", "get_bs_month_days", "get_bs_year_range",
    # formatting
    "format_bs_date", "parse_bs_date", "format_bs_datetime", "parse_bs_datetime",
    # misc helpers
    "difference_between_bs_dates", "add_days_to_bs_date", "subtract_days_from_bs_date",
    "get_current_bs_date", "get_current_bs_datetime", "bs_date_to_ordinal", "ordinal_to_bs_date",
    "is_leap_year_bs", "get_bs_week_number", "get_bs_quarter", "get_bs_fiscal_year",
    "get_bs_date_components", "get_bs_date_range", "get_bs_date_from_string",
    "bs_date_to_timestamp", "timestamp_to_bs_date", "bs_datetime_to_timestamp", "timestamp_to_bs_datetime",
    "get_bs_month_name", "get_bs_weekday_name",
]

def get_bs_year_range():
    """Get the range of supported BS years."""
    return (MIN_BS_YEAR, MAX_BS_YEAR)

def get_bs_month_name(bs_month):
    """Get the Nepali name of the BS month."""
    if not isinstance(bs_month, int):
        raise TypeError("BS month must be an integer")
    if 1 <= bs_month <= 12:
        return BS_MONTH_NAMES[bs_month - 1]
    raise ValueError(f"Invalid BS month: {bs_month}. Must be between 1 and 12")

def get_bs_weekday_name(weekday):
    """Get the Nepali name of the weekday."""
    if not isinstance(weekday, int):
        raise TypeError("Weekday must be an integer")
    if 0 <= weekday <= 6:
        return BS_WEEKDAY_NAMES[weekday]
    raise ValueError(f"Invalid weekday: {weekday}. Must be between 0 and 6")

def add_days_to_bs_date(bs_year, bs_month, bs_day, days_to_add):
    """Add days to a BS date."""
    ad_date = bs_to_ad(bs_year, bs_month, bs_day)
    new_ad_date = ad_date + datetime.timedelta(days=days_to_add)
    return ad_to_bs(new_ad_date)

def subtract_days_from_bs_date(bs_year, bs_month, bs_day, days_to_subtract):
    """Subtract days from a BS date."""
    ad_date = bs_to_ad(bs_year, bs_month, bs_day)
    new_ad_date = ad_date - datetime.timedelta(days=days_to_subtract)
    return ad_to_bs(new_ad_date)

def difference_between_bs_dates(bs_date1, bs_date2):
    """Calculate difference in days between two BS dates."""
    ad_date1 = bs_to_ad(*bs_date1)
    ad_date2 = bs_to_ad(*bs_date2)
    return (ad_date2 - ad_date1).days

def get_current_bs_date():
    """Get current BS date."""
    ad_date = datetime.date.today()
    return ad_to_bs(ad_date)

def get_current_bs_datetime():
    """Get current BS date and time."""
    now = datetime.datetime.now()
    bs_date = ad_to_bs(now.date())
    return bs_date + (now.hour, now.minute, now.second)

def bs_date_to_ordinal(bs_year, bs_month, bs_day):
    """Convert BS date to ordinal number."""
    ad_date = bs_to_ad(bs_year, bs_month, bs_day)
    return ad_date.toordinal()

def ordinal_to_bs_date(ordinal):
    """Convert ordinal number to BS date."""
    ad_date = datetime.date.fromordinal(ordinal)
    return ad_to_bs(ad_date)

def is_leap_year_bs(bs_year):
    """Check if BS year is a leap year (simplified)."""
    if bs_year < MIN_BS_YEAR or bs_year > MAX_BS_YEAR:
        raise ValueError("BS year out of supported range")
    ad_date = bs_to_ad(bs_year, 1, 1)
    ad_year = ad_date.year
    return (ad_year % 4 == 0 and ad_year % 100 != 0) or (ad_year % 400 == 0)

def get_bs_week_number(bs_year, bs_month, bs_day):
    """Get ISO week number for BS date."""
    ad_date = bs_to_ad(bs_year, bs_month, bs_day)
    return ad_date.isocalendar()[1]

def get_bs_quarter(bs_month):
    """Get quarter for BS month."""
    if 1 <= bs_month <= 3:
        return 1
    elif 4 <= bs_month <= 6:
        return 2
    elif 7 <= bs_month <= 9:
        return 3
    elif 10 <= bs_month <= 12:
        return 4
    else:
        raise ValueError("Invalid BS month")

def get_bs_fiscal_year(bs_year, bs_month):
    """Get fiscal year for BS date (starts in Ashwin)."""
    if bs_month >= 7:
        start_year = bs_year
        end_year = bs_year + 1
    else:
        start_year = bs_year - 1
        end_year = bs_year
    return f"{start_year}-{end_year}"

def get_bs_date_components(bs_year, bs_month, bs_day):
    """Get BS date components as dictionary."""
    if not is_valid_bs_date(bs_year, bs_month, bs_day):
        raise ValueError("Invalid BS date")
    ad_date = bs_to_ad(bs_year, bs_month, bs_day)
    weekday = (ad_date.weekday() + 1) % 7
    return {
        "year": bs_year,
        "month": bs_month,
        "day": bs_day,
        "month_name": get_bs_month_name(bs_month),
        "weekday_name": get_bs_weekday_name(weekday)
    }

def get_bs_date_range(start_bs_date, end_bs_date):
    """Generate list of BS dates between two dates."""
    start_ad_date = bs_to_ad(*start_bs_date)
    end_ad_date = bs_to_ad(*end_bs_date)
    if start_ad_date > end_ad_date:
        raise ValueError("Start date must be before or equal to end date")
    delta_days = (end_ad_date - start_ad_date).days
    bs_dates = []
    for i in range(delta_days + 1):
        current_ad_date = start_ad_date + datetime.timedelta(days=i)
        bs_dates.append(ad_to_bs(current_ad_date))
    return bs_dates

def get_bs_date_from_string(date_string):
    """Parse BS date from string in various formats."""
    common_formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
    ]
    for fmt in common_formats:
        try:
            return parse_bs_date(date_string, fmt)
        except ValueError:
            continue
    raise ValueError("Date string does not match any known format")

# Timestamp helpers
def bs_date_to_timestamp(bs_year, bs_month, bs_day):
    """Convert BS date to Unix timestamp."""
    ad_date = bs_to_ad(bs_year, bs_month, bs_day)
    return int(datetime.datetime(ad_date.year, ad_date.month, ad_date.day).timestamp())

def timestamp_to_bs_date(ts):
    """Convert Unix timestamp to BS date."""
    ad_dt = datetime.datetime.fromtimestamp(ts)
    return ad_to_bs(ad_dt.date())

def bs_datetime_to_timestamp(bs_year, bs_month, bs_day, hour=0, minute=0, second=0):
    """Convert BS datetime to Unix timestamp."""
    ad_date = bs_to_ad(bs_year, bs_month, bs_day)
    ad_dt = datetime.datetime(ad_date.year, ad_date.month, ad_date.day, hour, minute, second)
    return int(ad_dt.timestamp())

def timestamp_to_bs_datetime(ts):
    """Convert Unix timestamp to BS datetime."""
    ad_dt = datetime.datetime.fromtimestamp(ts)
    y, m, d = ad_to_bs(ad_dt.date())
    return (y, m, d, ad_dt.hour, ad_dt.minute, ad_dt.second)

