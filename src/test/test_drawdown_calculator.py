"""Tests de la logique pure de DrawdownCalculator (sans base de données)."""

from drawdown_calculator import DrawdownCalculator

calc = DrawdownCalculator({})


def test_empty_prices_returns_empty():
    assert calc.calculate_drawdown_series([]) == []


def test_monotonic_increase_has_no_drawdown():
    # Chaque nouveau prix est un plus-haut -> drawdown nul partout.
    assert calc.calculate_drawdown_series([100, 110, 121]) == [0, 0, 0]


def test_single_drop_gives_expected_percentage():
    # Sommet 100 puis chute à 50 -> drawdown de 50 %.
    assert calc.calculate_drawdown_series([100, 50]) == [0.0, 50.0]


def test_peak_then_partial_recovery():
    # Sommet 200, retour à 100 -> (200-100)/200 = 50 %.
    assert calc.calculate_drawdown_series([100, 200, 100]) == [0, 0, 50]


def test_drawdown_is_never_negative():
    series = calc.calculate_drawdown_series([100, 120, 90, 130, 70])
    assert all(d >= 0 for d in series)


def test_length_matches_input():
    prices = [10, 20, 15, 30, 5]
    assert len(calc.calculate_drawdown_series(prices)) == len(prices)
