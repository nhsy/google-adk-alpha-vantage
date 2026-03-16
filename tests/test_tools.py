import pytest
from datetime import datetime, timezone
from unittest.mock import patch
from src.agent.tools import get_current_datetime, DateTimeResult


FIXED_DT = datetime(2026, 3, 16, 14, 30, 0, tzinfo=timezone.utc)


def _call() -> DateTimeResult:
    with patch("src.agent.tools.datetime") as mock_dt:
        mock_dt.now.return_value = FIXED_DT
        mock_dt.now.side_effect = None
        # Allow strftime/etc to pass through to the real datetime
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        return get_current_datetime()


def test_get_current_datetime_fields():
    result = get_current_datetime()
    expected_fields = {
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
    assert expected_fields == set(result.model_fields_set)


@pytest.mark.parametrize(
    "field, expected_type",
    [
        ("iso", str),
        ("date", str),
        ("year", int),
        ("month", int),
        ("month_name", str),
        ("day", int),
        ("weekday", str),
        ("time", str),
        ("timezone", str),
    ],
)
def test_get_current_datetime_types(field, expected_type):
    result = get_current_datetime()
    assert isinstance(getattr(result, field), expected_type)


@pytest.mark.parametrize(
    "field, expected_value",
    [
        ("year", 2026),
        ("month", 3),
        ("day", 16),
        ("date", "2026-03-16"),
        ("month_name", "March"),
        ("weekday", "Monday"),
        ("time", "14:30:00"),
        ("timezone", "UTC"),
    ],
)
def test_get_current_datetime_values(field, expected_value):
    result = _call()
    assert getattr(result, field) == expected_value


def test_get_current_datetime_iso_value():
    result = _call()
    assert result.iso.startswith("2026-03-16T14:30:00")


def test_get_current_datetime_iso_format():
    result = get_current_datetime()
    # Should be parseable as ISO 8601
    parsed = datetime.fromisoformat(result.iso)
    assert parsed.tzinfo is not None


def test_get_current_datetime_date_format():
    result = get_current_datetime()
    parts = result.date.split("-")
    assert len(parts) == 3
    assert parts[0] == str(result.year)
    assert parts[1] == str(result.month).zfill(2)
    assert parts[2] == str(result.day).zfill(2)


def test_get_current_datetime_month_range():
    result = get_current_datetime()
    assert 1 <= result.month <= 12


def test_get_current_datetime_day_range():
    result = get_current_datetime()
    assert 1 <= result.day <= 31
