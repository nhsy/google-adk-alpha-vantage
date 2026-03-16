from datetime import datetime, timezone
from unittest.mock import patch
from src.agent.tools import get_current_datetime


FIXED_DT = datetime(2026, 3, 16, 14, 30, 0, tzinfo=timezone.utc)


def _call() -> dict:
    with patch("src.agent.tools.datetime") as mock_dt:
        mock_dt.now.return_value = FIXED_DT
        mock_dt.now.side_effect = None
        # Allow strftime/etc to pass through to the real datetime
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        return get_current_datetime()


def test_get_current_datetime_keys():
    result = get_current_datetime()
    expected_keys = {
        "iso",
        "date",
        "year",
        "month",
        "month_name",
        "day",
        "weekday",
        "time",
        "timezone",
    }
    assert expected_keys == set(result.keys())


def test_get_current_datetime_types():
    result = get_current_datetime()
    assert isinstance(result["iso"], str)
    assert isinstance(result["year"], int)
    assert isinstance(result["month"], int)
    assert isinstance(result["day"], int)
    assert isinstance(result["date"], str)
    assert isinstance(result["month_name"], str)
    assert isinstance(result["weekday"], str)
    assert isinstance(result["time"], str)
    assert result["timezone"] == "UTC"


def test_get_current_datetime_values():
    with patch("src.agent.tools.datetime") as mock_dt:
        mock_dt.now.return_value = FIXED_DT
        result = get_current_datetime()

    assert result["year"] == 2026
    assert result["month"] == 3
    assert result["day"] == 16
    assert result["date"] == "2026-03-16"
    assert result["month_name"] == "March"
    assert result["weekday"] == "Monday"
    assert result["time"] == "14:30:00"
    assert result["timezone"] == "UTC"
    assert result["iso"].startswith("2026-03-16T14:30:00")


def test_get_current_datetime_iso_format():
    result = get_current_datetime()
    # Should be parseable as ISO 8601
    parsed = datetime.fromisoformat(result["iso"])
    assert parsed.tzinfo is not None


def test_get_current_datetime_date_format():
    result = get_current_datetime()
    parts = result["date"].split("-")
    assert len(parts) == 3
    assert parts[0] == str(result["year"])
    assert parts[1] == str(result["month"]).zfill(2)
    assert parts[2] == str(result["day"]).zfill(2)


def test_get_current_datetime_month_range():
    result = get_current_datetime()
    assert 1 <= result["month"] <= 12


def test_get_current_datetime_day_range():
    result = get_current_datetime()
    assert 1 <= result["day"] <= 31
