"""Tests de la logique de seuils PURE (evaluate_metrics), sans base de données."""

from checks import evaluate_metrics


def _good_silver(**overrides):
    base = {
        "row_count": 1000,
        "null_prices": 0,
        "non_positive_prices": 0,
        "distinct_coins": 5,
        "duplicate_buckets": 0,
        "staleness_days": 1.0,
    }
    base.update(overrides)
    return base


def _good_gold(**overrides):
    base = {
        "gold_volatility_rows": 7,
        "gold_sharpe_rows": 5,
        "gold_drawdown_rows": 7,
        "gold_correlation_matrix_rows": 10,
        "correlation_out_of_range": 0,
    }
    base.update(overrides)
    return base


def test_all_good_has_no_error_no_warning():
    errors, warnings = evaluate_metrics(_good_silver(), _good_gold())
    assert errors == []
    assert warnings == []


def test_empty_silver_is_error():
    errors, _ = evaluate_metrics(_good_silver(row_count=0), _good_gold())
    assert any("vide" in e for e in errors)


def test_null_prices_is_error():
    errors, _ = evaluate_metrics(_good_silver(null_prices=3), _good_gold())
    assert any("NULL" in e for e in errors)


def test_non_positive_prices_is_error():
    errors, _ = evaluate_metrics(_good_silver(non_positive_prices=2), _good_gold())
    assert any("<= 0" in e for e in errors)


def test_duplicate_buckets_is_error():
    errors, _ = evaluate_metrics(_good_silver(duplicate_buckets=4), _good_gold())
    assert any("doublons" in e for e in errors)


def test_too_few_coins_is_error():
    errors, _ = evaluate_metrics(_good_silver(distinct_coins=1), _good_gold(), min_coins=3)
    assert any("crypto" in e for e in errors)


def test_staleness_is_warning_not_error():
    errors, warnings = evaluate_metrics(
        _good_silver(staleness_days=900.0), _good_gold(), max_staleness_days=400.0
    )
    assert errors == []
    assert any("ancienne" in w for w in warnings)


def test_missing_staleness_is_warning():
    _, warnings = evaluate_metrics(_good_silver(staleness_days=None), _good_gold())
    assert any("fraîcheur" in w for w in warnings)


def test_empty_gold_table_is_error():
    errors, _ = evaluate_metrics(_good_silver(), _good_gold(gold_sharpe_rows=0))
    assert any("gold_sharpe" in e and "vide" in e for e in errors)


def test_correlation_out_of_range_is_error():
    errors, _ = evaluate_metrics(_good_silver(), _good_gold(correlation_out_of_range=2))
    assert any("hors [-1, 1]" in e for e in errors)


def test_errors_accumulate_across_layers():
    errors, _ = evaluate_metrics(
        _good_silver(null_prices=1, distinct_coins=1),
        _good_gold(gold_volatility_rows=0),
    )
    assert len(errors) >= 3
