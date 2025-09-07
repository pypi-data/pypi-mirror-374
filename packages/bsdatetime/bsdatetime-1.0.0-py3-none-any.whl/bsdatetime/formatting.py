"""Formatting and parsing for BS dates and datetimes."""
from __future__ import annotations
import datetime as _dt
from .config import BS_MONTH_NAMES, BS_WEEKDAY_NAMES
from .conversion import bs_to_ad
from .validation import is_valid_bs_date

__all__ = [
    "format_bs_date",
    "parse_bs_date",
    "format_bs_datetime", 
    "parse_bs_datetime",
]

def _weekday_to_custom(ad_weekday: int) -> int:
    """Convert Python weekday to custom Sunday=0 mapping."""
    return (ad_weekday + 1) % 7

def format_bs_date(bs_year: int, bs_month: int, bs_day: int, fmt: str = "%Y-%m-%d") -> str:
    """Format a BS date according to the given format string."""
    ad_date = bs_to_ad(bs_year, bs_month, bs_day)
    weekday = _weekday_to_custom(ad_date.weekday())
    replacements = {
        "%Y": f"{bs_year:04d}",
        "%m": f"{bs_month:02d}",
        "%d": f"{bs_day:02d}",
        "%B": BS_MONTH_NAMES[bs_month - 1],
        "%A": BS_WEEKDAY_NAMES[weekday],
    }
    out = fmt
    for k, v in replacements.items():
        out = out.replace(k, v)
    return out

def parse_bs_date(text: str, fmt: str = "%Y-%m-%d"):
    """Parse a BS date string according to the given format."""
    fmt_parts = fmt.split('-')
    txt_parts = text.split('-')
    if len(fmt_parts) != len(txt_parts):
        raise ValueError("Date string does not match format")
    y = m = d = None
    for f, t in zip(fmt_parts, txt_parts):
        if f == "%Y":
            y = int(t)
        elif f == "%m":
            m = int(t)
        elif f == "%d":
            d = int(t)
        elif f == "%B":
            if t in BS_MONTH_NAMES:
                m = BS_MONTH_NAMES.index(t) + 1
            else:
                raise ValueError("Invalid month name")
        else:
            raise ValueError("Unsupported token")
    if None in (y, m, d):
        raise ValueError("Incomplete date")
    if not is_valid_bs_date(y, m, d):
        raise ValueError("Invalid BS date")
    return (y, m, d)

def format_bs_datetime(bs_year: int, bs_month: int, bs_day: int, hour: int=0, minute: int=0, second: int=0, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a BS datetime according to the given format string."""
    date_fmt, time_fmt = (fmt.split(' ', 1) + [""])[:2] if ' ' in fmt else (fmt, "")
    date_part = format_bs_date(bs_year, bs_month, bs_day, date_fmt)
    if not time_fmt:
        return date_part
    rep = {
        "%H": f"{hour:02d}",
        "%M": f"{minute:02d}",
        "%S": f"{second:02d}",
    }
    time_out = time_fmt
    for k, v in rep.items():
        time_out = time_out.replace(k, v)
    return f"{date_part} {time_out}".strip()

def parse_bs_datetime(text: str, fmt: str = "%Y-%m-%d %H:%M:%S"):
    """Parse a BS datetime string according to the given format."""
    if ' ' not in fmt:
        y, m, d = parse_bs_date(text, fmt)
        return (y, m, d, 0, 0, 0)
    date_fmt, time_fmt = fmt.split(' ', 1)
    date_part, time_part = text.split(' ', 1)
    y, m, d = parse_bs_date(date_part, date_fmt)
    t_tokens = time_fmt.split(':')
    v_tokens = time_part.split(':')
    if len(t_tokens) != len(v_tokens):
        raise ValueError("Time portion mismatch")
    hour = minute = second = 0
    for f, v in zip(t_tokens, v_tokens):
        if f == "%H":
            hour = int(v)
        elif f == "%M":
            minute = int(v)
        elif f == "%S":
            second = int(v)
        else:
            raise ValueError("Unsupported time token")
    return (y, m, d, hour, minute, second)
