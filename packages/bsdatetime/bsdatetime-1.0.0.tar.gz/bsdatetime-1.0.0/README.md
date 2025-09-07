# bsdatetime

Lightweight, dependency‑free Bikram Sambat (Nepali) calendar utilities for Python.

Documentation: https://rajendra-katuwal.github.io/bsdatetime.docs/

## What it does
* Convert between Gregorian (AD) and Bikram Sambat (BS)
* Format / parse BS dates (localized month + weekday names)
* Validate dates, get fiscal year, week number, ranges
* Provide current BS date/time helpers

## Install
```bash
pip install bsdatetime
```

## Quick start
```python
import datetime, bsdatetime as bs

ad = datetime.date(2024, 12, 25)
bs_tuple = bs.ad_to_bs(ad)          # (2081, 9, 9)
ad_back = bs.bs_to_ad(*bs_tuple)    # 2024-12-25
text = bs.format_bs_date(*bs_tuple, "%B %d, %Y")  # भदौ 09, 2081
current_bs = bs.utils.get_current_bs_date()
```

Core API (most used)
* ad_to_bs(date)
* bs_to_ad(y, m, d)
* format_bs_date(y, m, d, fmt)
* parse_bs_date(text, fmt)
* is_valid_bs_date(y, m, d)
* utils.get_current_bs_date()

Supported range: BS 1975–2100 (≈ AD 1918–2043)

## Django?
Use the companion package for model fields:
```bash
pip install django-bsdatetime
```

## License
MIT
