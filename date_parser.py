"""
Flexible date parsing: accepts March, Mar, 03, 3, YYYY-MM-DD, etc.
Returns YYYY-MM-DD for storage and correct sorting.
"""
from datetime import datetime


# Formats tried in order. Use current year/month/day where needed.
FORMATS = [
    "%Y-%m-%d",           # 2025-03-15
    "%Y/%m/%d",
    "%m/%d/%Y",           # 03/15/2025, 3/15/2025
    "%m-%d-%Y",
    "%d/%m/%Y",           # 15/03/2025
    "%d-%m-%Y",
    "%B %d %Y",           # March 15 2025
    "%b %d %Y",           # Mar 15 2025
    "%B %d, %Y",          # March 15, 2025
    "%b %d, %Y",          # Mar 15, 2025
    "%d %B %Y",           # 15 March 2025
    "%d %b %Y",           # 15 Mar 2025
    "%B %d",              # March 15 -> current year
    "%b %d",              # Mar 15
    "%m/%d",              # 03/15, 3/15
    "%d/%m",              # 15/03
    "%m-%d",
    "%d-%m",
    "%B %Y",              # March 2025 -> 1st
    "%b %Y",
    "%m/%Y",
    "%Y/%m",
]


def normalize_date(value: str):
    """
    Parse flexible date string (March, Mar, 03, 3, 2025-03-15, etc.)
    and return YYYY-MM-DD or None if unparseable.
    """
    if not value or not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None
    now = datetime.now()
    for fmt in FORMATS:
        try:
            dt = datetime.strptime(raw, fmt)
            # Fill missing year/month/day from today
            if "%Y" not in fmt and "%y" not in fmt:
                dt = dt.replace(year=now.year)
            if "%m" not in fmt and "%b" not in fmt and "%B" not in fmt:
                dt = dt.replace(month=now.month)
            if "%d" not in fmt:
                dt = dt.replace(day=1)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    # Try numeric: "3" or "03" as day of current month, or month (1-12) = 1st of that month
    if raw.isdigit():
        n = int(raw)
        if 1 <= n <= 31:
            try:
                dt = now.replace(day=n)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
        if 1 <= n <= 12:
            try:
                dt = now.replace(month=n, day=1)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
    return None
