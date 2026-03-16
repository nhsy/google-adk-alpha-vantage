from datetime import datetime, timezone
from pydantic import BaseModel


class DateTimeResult(BaseModel):
    iso: str
    date: str
    year: int
    month: int
    month_name: str
    day: int
    weekday: str
    time: str
    timezone: str


def get_current_datetime() -> DateTimeResult:
    """Returns the current UTC date and time broken into useful components.

    Returns:
        A dictionary containing:
            - iso: ISO 8601 datetime string (e.g. "2026-03-16T14:30:00+00:00")
            - date: Full date string (e.g. "2026-03-16")
            - year: Current year as an integer (e.g. 2026)
            - month: Current month as an integer 1-12 (e.g. 3)
            - month_name: Full month name (e.g. "March")
            - day: Current day of the month as an integer (e.g. 16)
            - weekday: Full weekday name (e.g. "Monday")
            - time: Current time in HH:MM:SS format (e.g. "14:30:00")
            - timezone: Always "UTC"
    """
    now = datetime.now(tz=timezone.utc)
    return DateTimeResult(
        iso=now.isoformat(),
        date=now.strftime("%Y-%m-%d"),
        year=now.year,
        month=now.month,
        month_name=now.strftime("%B"),
        day=now.day,
        weekday=now.strftime("%A"),
        time=now.strftime("%H:%M:%S"),
        timezone="UTC",
    )
