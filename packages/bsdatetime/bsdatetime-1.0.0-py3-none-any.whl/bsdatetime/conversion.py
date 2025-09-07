"""Conversion between AD (Gregorian) and BS (Bikram Sambat) calendars."""
from __future__ import annotations
import datetime as _dt
from .config import BASE_AD, BASE_BS, BS_YEARS, MIN_BS_YEAR, MAX_BS_YEAR

__all__ = ["ad_to_bs", "bs_to_ad"]

def ad_to_bs(ad_date: _dt.date):
    """Convert an AD (Gregorian) date to a BS date tuple (year, month, day).
    
    Args:
        ad_date: A datetime.date object in Gregorian calendar
        
    Returns:
        tuple: (year, month, day) in Bikram Sambat calendar
        
    Raises:
        ValueError: If the date is outside the supported range
        TypeError: If ad_date is not a datetime.date object
    """
    if not isinstance(ad_date, _dt.date):
        raise TypeError("ad_date must be a datetime.date object")
        
    days = (ad_date - BASE_AD).days
    year, month, day = BASE_BS
    
    # Handle negative days (dates before BASE_AD)
    if days < 0:
        days = abs(days)
        while days > 0:
            day -= 1
            if day < 1:
                month -= 1
                if month < 1:
                    month = 12
                    year -= 1
                    if year < MIN_BS_YEAR:
                        raise ValueError(f"Date {ad_date} is before supported BS range")
                day = BS_YEARS[year][month - 1]
            days -= 1
    else:
        # Handle positive days (dates after BASE_AD)
        while days > 0:
            if year > MAX_BS_YEAR:
                raise ValueError(f"Date {ad_date} is after supported BS range")
            month_days = BS_YEARS[year][month - 1]
            if day + days <= month_days:
                day += days
                days = 0
            else:
                days -= (month_days - day + 1)
                day = 1
                month += 1
                if month > 12:
                    month = 1
                    year += 1
    
    return (year, month, day)

def bs_to_ad(bs_year: int, bs_month: int, bs_day: int) -> _dt.date:
    """Convert a BS date (y,m,d) to an AD date object.
    
    Args:
        bs_year: Bikram Sambat year
        bs_month: Bikram Sambat month (1-12)
        bs_day: Bikram Sambat day
        
    Returns:
        datetime.date: Corresponding Gregorian date
        
    Raises:
        ValueError: If the BS date is invalid or outside supported range
        TypeError: If inputs are not integers
    """
    # Input validation
    if not all(isinstance(x, int) for x in [bs_year, bs_month, bs_day]):
        raise TypeError("BS date components must be integers")
        
    if bs_year < MIN_BS_YEAR or bs_year > MAX_BS_YEAR:
        raise ValueError(f"BS year {bs_year} is outside supported range ({MIN_BS_YEAR}-{MAX_BS_YEAR})")
        
    if bs_month < 1 or bs_month > 12:
        raise ValueError(f"BS month {bs_month} must be between 1 and 12")
        
    if bs_year not in BS_YEARS:
        raise ValueError(f"No calendar data available for BS year {bs_year}")
        
    if bs_day < 1 or bs_day > BS_YEARS[bs_year][bs_month - 1]:
        raise ValueError(f"BS day {bs_day} is invalid for month {bs_month} of year {bs_year}")
    
    ad_date = BASE_AD
    year, month, day = BASE_BS
    
    # Prevent infinite loops with a safety counter
    max_iterations = 50000  # Roughly 137 years worth of days
    iterations = 0
    
    while (year, month, day) != (bs_year, bs_month, bs_day):
        iterations += 1
        if iterations > max_iterations:
            raise ValueError("Conversion exceeded maximum iterations - possible infinite loop")
            
        ad_date += _dt.timedelta(days=1)
        day += 1
        if day > BS_YEARS[year][month - 1]:
            day = 1
            month += 1
            if month > 12:
                month = 1
                year += 1
                if year > MAX_BS_YEAR:
                    raise ValueError("BS date is outside supported range")
    
    return ad_date
