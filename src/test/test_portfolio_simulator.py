"""Tests de la fonction pure to_naive_utc de portfolio_simulator."""

from datetime import datetime, timedelta, timezone

from portfolio_simulator import to_naive_utc


def test_aware_utc_becomes_naive():
    dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    out = to_naive_utc(dt)
    assert out.tzinfo is None
    assert out == datetime(2024, 1, 1, 12, 0)


def test_aware_offset_is_converted_to_utc():
    # +02:00 à 12h -> 10h UTC, sans tzinfo.
    dt = datetime(2024, 1, 1, 12, 0, tzinfo=timezone(timedelta(hours=2)))
    out = to_naive_utc(dt)
    assert out.tzinfo is None
    assert out == datetime(2024, 1, 1, 10, 0)


def test_naive_datetime_is_unchanged():
    dt = datetime(2024, 1, 1, 12, 0)
    out = to_naive_utc(dt)
    assert out.tzinfo is None
    assert out == dt
