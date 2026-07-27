"""Tests de la logique pure de CorrelationCalculator (sans base de données)."""

import pytest

from correlation_calculator import CorrelationCalculator

calc = CorrelationCalculator({})


def test_returns_series_basic():
    assert calc.get_returns_series([100, 110]) == [pytest.approx(10.0)]


def test_returns_series_needs_two_points():
    assert calc.get_returns_series([100]) == []
    assert calc.get_returns_series([]) == []


def test_returns_series_up_then_down():
    result = calc.get_returns_series([100, 110, 99])
    assert result == [pytest.approx(10.0), pytest.approx(-10.0)]


def test_pearson_perfect_positive():
    assert CorrelationCalculator._pearson([1, 2, 3], [2, 4, 6]) == pytest.approx(1.0)


def test_pearson_perfect_negative():
    assert CorrelationCalculator._pearson([1, 2, 3], [3, 2, 1]) == pytest.approx(-1.0)


def test_pearson_constant_series_is_zero():
    # Variance nulle sur une série -> corrélation définie à 0.
    assert CorrelationCalculator._pearson([1, 2, 3], [5, 5, 5]) == 0.0


def test_pearson_too_few_points_is_zero():
    assert CorrelationCalculator._pearson([1], [2]) == 0.0


@pytest.mark.parametrize(
    "corr,label",
    [
        (0.95, "Very Strong"),
        (-0.95, "Very Strong"),  # l'interprétation se base sur la valeur absolue
        (0.80, "Strong"),
        (0.50, "Moderate"),
        (0.25, "Weak"),
        (0.05, "Very Weak / None"),
    ],
)
def test_interpret_correlation_thresholds(corr, label):
    assert calc._interpret_correlation(corr) == label


@pytest.mark.parametrize(
    "corr,prefix",
    [
        (-0.6, "Excellent"),
        (-0.2, "Good"),
        (0.2, "Moderate"),
        (0.5, "Limited"),
        (0.9, "Poor"),
    ],
)
def test_diversification_benefit_thresholds(corr, prefix):
    assert calc._diversification_benefit(corr).startswith(prefix)
