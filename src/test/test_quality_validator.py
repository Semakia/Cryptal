"""Tests du validateur qualité à l'ingestion (validate_record)."""

from datetime import datetime, timedelta, timezone

import pytest

from validator import is_valid, parse_timestamp, validate_record


def _valid_message(**overrides):
    base = {
        "source": "coingecko",
        "currency": "usd,eur,gbp",
        "coin_id": "bitcoin",
        "price_usd": 68000.0,
        "price_eur": 63000.0,
        "price_gbp": 54000.0,
        "change_24h": 1.5,
        "market_cap": 1_300_000_000_000,
        "timestamp": "2024-01-01T12:00:00",
    }
    base.update(overrides)
    return base


def test_valid_message_passes():
    assert validate_record(_valid_message()) == []
    assert is_valid(_valid_message()) is True


def test_optional_fields_may_be_none():
    msg = _valid_message(price_eur=None, price_gbp=None, change_24h=None, market_cap=None)
    assert validate_record(msg) == []


@pytest.mark.parametrize("bad_coin", [None, "", "Bitcoin!", "x" * 51, 123])
def test_invalid_coin_id_is_rejected(bad_coin):
    assert validate_record(_valid_message(coin_id=bad_coin)) != []


@pytest.mark.parametrize("bad_price", [None, 0, -1, float("nan"), float("inf"), "68000", True])
def test_invalid_price_usd_is_rejected(bad_price):
    errors = validate_record(_valid_message(price_usd=bad_price))
    assert any("price_usd" in e for e in errors)


def test_negative_optional_price_is_rejected():
    assert any("price_eur" in e for e in validate_record(_valid_message(price_eur=-5)))


@pytest.mark.parametrize("bad_change", [-150, 20000, float("nan")])
def test_out_of_band_change_is_rejected(bad_change):
    assert any("change_24h" in e for e in validate_record(_valid_message(change_24h=bad_change)))


def test_negative_market_cap_is_rejected():
    assert any("market_cap" in e for e in validate_record(_valid_message(market_cap=-1)))


@pytest.mark.parametrize("bad_ts", [None, "", "not-a-date", 42])
def test_invalid_timestamp_is_rejected(bad_ts):
    assert any("timestamp" in e for e in validate_record(_valid_message(timestamp=bad_ts)))


def test_future_timestamp_is_rejected():
    future = (datetime.utcnow() + timedelta(days=2)).isoformat()
    assert any("futur" in e for e in validate_record(_valid_message(timestamp=future)))


def test_multiple_errors_are_accumulated():
    msg = _valid_message(coin_id="", price_usd=-1, market_cap=-2)
    assert len(validate_record(msg)) >= 3


def test_non_dict_message_is_rejected():
    assert validate_record("not a dict") == ["message n'est pas un dict"]


def test_parse_timestamp_handles_z_suffix_and_offset():
    assert parse_timestamp("2024-01-01T12:00:00Z") == datetime(2024, 1, 1, 12, 0)
    # +02:00 -> 10:00 UTC naïf
    aware = datetime(2024, 1, 1, 12, 0, tzinfo=timezone(timedelta(hours=2)))
    assert parse_timestamp(aware) == datetime(2024, 1, 1, 10, 0)
    assert parse_timestamp("garbage") is None
