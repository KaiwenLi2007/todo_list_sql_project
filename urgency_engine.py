"""
Urgency Engine: computes urgency_score from deadline and est_hours.
Runs on Create and Update. Uses time delta and buffer logic.
Returns "1-HIGH", "2-MEDIUM", or "3-LOW".
Also exposes buffer_hours for reliable sorting (smaller = more urgent).
"""
from datetime import datetime

# Normalize flexible dates (March 17, Mar 20, etc.) to YYYY-MM-DD for parsing
try:
    from date_parser import normalize_date
except ImportError:
    normalize_date = None


def _normalize_deadline(deadline: str):
    """Return YYYY-MM-DD or None. Handles March, Mar, 03, etc. if date_parser available."""
    if not deadline or not deadline.strip():
        return None
    s = deadline.strip()
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        pass
    if normalize_date:
        return normalize_date(s)
    return None


def get_buffer_hours(deadline: str, est_hours: float) -> float:
    """
    Return buffer hours: (deadline - now) in hours minus est_hours.
    Negative = overdue or no buffer. Used for sorting (asc = most urgent first).
    """
    if est_hours is None:
        return float("inf")
    normalized = _normalize_deadline(deadline)
    if not normalized:
        return float("inf")
    try:
        due_date = datetime.strptime(normalized, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return float("inf")
    deadline_datetime = datetime.combine(due_date, datetime.max.time())
    current_datetime = datetime.now()
    delta = deadline_datetime - current_datetime
    available_hours = delta.total_seconds() / 3600.0
    return available_hours - est_hours


def compute_urgency(deadline: str, est_hours: float) -> str:
    """
    - Due within 3 days AND requires 6+ hours → HIGH (urgent).
    - Else: buffer = (deadline - now) in hours minus est_hours.
      HIGH: buffer < 12h; MEDIUM: buffer < 48h; LOW: 48h+.
    """
    normalized = _normalize_deadline(deadline)
    if not normalized or est_hours is None:
        return "2-MEDIUM"
    try:
        due_date = datetime.strptime(normalized, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return "2-MEDIUM"
    deadline_datetime = datetime.combine(due_date, datetime.max.time())
    current_datetime = datetime.now()
    delta = deadline_datetime - current_datetime
    available_hours = delta.total_seconds() / 3600.0

    # Rule: due in 3 days (72h) and requires 6+ hours → urgent (HIGH)
    if available_hours <= 72 and est_hours >= 6:
        return "1-HIGH"

    buffer_hours = available_hours - est_hours
    if buffer_hours < 12:
        return "1-HIGH"
    if buffer_hours < 48:
        return "2-MEDIUM"
    return "3-LOW"
