"""Tests des modèles Pydantic de l'API (validation, coercition)."""

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from models import BestEntryPointRequest, PnLSimulationRequest, PriceData


def _price(**overrides):
    base = dict(id=1, coin_id="bitcoin", price_usd=100.0, timestamp=datetime(2024, 1, 1))
    base.update(overrides)
    return PriceData(**base)


def test_market_cap_decimal_is_coerced_to_int():
    p = _price(market_cap=Decimal("50000"))
    assert p.market_cap == 50000
    assert isinstance(p.market_cap, int)


def test_market_cap_none_is_allowed():
    assert _price(market_cap=None).market_cap is None


def test_pnl_request_amount_must_be_positive():
    with pytest.raises(ValidationError):
        PnLSimulationRequest(crypto="bitcoin", amount=0, purchase_date=datetime(2024, 1, 1))
    with pytest.raises(ValidationError):
        PnLSimulationRequest(crypto="bitcoin", amount=-10, purchase_date=datetime(2024, 1, 1))


def test_pnl_request_valid():
    req = PnLSimulationRequest(
        crypto="bitcoin", amount=1000.0, purchase_date=datetime(2024, 1, 1)
    )
    assert req.amount == 1000.0
    assert req.crypto == "bitcoin"


def test_best_entry_lookback_bounds_are_enforced():
    with pytest.raises(ValidationError):
        BestEntryPointRequest(crypto="ethereum", amount=100, lookback_days=0)
    with pytest.raises(ValidationError):
        BestEntryPointRequest(crypto="ethereum", amount=100, lookback_days=400)


def test_best_entry_lookback_defaults_to_30():
    assert BestEntryPointRequest(crypto="ethereum", amount=100).lookback_days == 30
