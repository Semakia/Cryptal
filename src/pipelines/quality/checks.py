"""Contrôles qualité au niveau dataset (couches silver & gold).

Séparés en deux responsabilités :
  - gather_* : collecte des métriques via SQL (nécessite une connexion) ;
  - evaluate_metrics : logique de seuils PURE (testable sans BDD).

Sévérités :
  - ERROR : brise le gate (données invalides/incomplètes qui nourrissent l'API) ;
  - WARN  : signalé seulement (ex. fraîcheur — la donnée démo est ancienne).
"""

from datetime import datetime


# --------------------------------------------------------------------------- #
# Collecte des métriques (SQL)
# --------------------------------------------------------------------------- #
def gather_silver_metrics(conn) -> dict:
    """Métriques sur crypto_prices_series (couche silver)."""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM crypto_prices_series")
        row_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM crypto_prices_series WHERE price_usd IS NULL")
        null_prices = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM crypto_prices_series WHERE price_usd <= 0")
        non_positive_prices = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT coin_id) FROM crypto_prices_series")
        distinct_coins = cur.fetchone()[0]

        cur.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT coin_id, time_bucket
                FROM crypto_prices_series
                GROUP BY coin_id, time_bucket
                HAVING COUNT(*) > 1
            ) d
            """
        )
        duplicate_buckets = cur.fetchone()[0]

        cur.execute("SELECT MAX(time_bucket) FROM crypto_prices_series")
        latest = cur.fetchone()[0]

    staleness_days = None
    if latest is not None:
        staleness_days = (datetime.utcnow() - latest).total_seconds() / 86400.0

    return {
        "row_count": row_count,
        "null_prices": null_prices,
        "non_positive_prices": non_positive_prices,
        "distinct_coins": distinct_coins,
        "duplicate_buckets": duplicate_buckets,
        "staleness_days": staleness_days,
    }


def gather_gold_metrics(conn) -> dict:
    """Métriques sur les tables gold qui nourrissent l'API."""
    metrics = {}
    with conn.cursor() as cur:
        for table in ("gold_volatility", "gold_sharpe", "gold_drawdown", "gold_correlation_matrix"):
            cur.execute(f"SELECT COUNT(*) FROM {table}")  # noqa: S608 (noms en dur, pas d'input)
            metrics[f"{table}_rows"] = cur.fetchone()[0]

        # Les corrélations doivent rester dans [-1, 1].
        cur.execute(
            "SELECT COUNT(*) FROM gold_correlation_matrix WHERE correlation < -1 OR correlation > 1"
        )
        metrics["correlation_out_of_range"] = cur.fetchone()[0]

    return metrics


# --------------------------------------------------------------------------- #
# Évaluation des seuils (pure)
# --------------------------------------------------------------------------- #
def evaluate_metrics(
    silver: dict,
    gold: dict,
    *,
    min_coins: int = 3,
    max_staleness_days: float = 400.0,
) -> tuple:
    """Évalue les métriques. Retourne (errors, warnings) : listes de messages.

    errors  -> le gate échoue (exit != 0)
    warnings -> signalé seulement
    """
    errors = []
    warnings = []

    # --- Silver : complétude & validité (bloquant) ---
    if silver.get("row_count", 0) <= 0:
        errors.append("silver.crypto_prices_series est vide")
    if silver.get("null_prices", 0) > 0:
        errors.append(f"silver: {silver['null_prices']} prix NULL")
    if silver.get("non_positive_prices", 0) > 0:
        errors.append(f"silver: {silver['non_positive_prices']} prix <= 0")
    if silver.get("duplicate_buckets", 0) > 0:
        errors.append(f"silver: {silver['duplicate_buckets']} doublons (coin_id, time_bucket)")
    if silver.get("distinct_coins", 0) < min_coins:
        errors.append(
            f"silver: seulement {silver.get('distinct_coins', 0)} crypto(s) (min {min_coins})"
        )

    # --- Silver : fraîcheur (non bloquant) ---
    staleness = silver.get("staleness_days")
    if staleness is None:
        warnings.append("silver: aucune donnée pour évaluer la fraîcheur")
    elif staleness > max_staleness_days:
        warnings.append(
            f"silver: donnée ancienne ({staleness:.1f} j > {max_staleness_days} j)"
        )

    # --- Gold : chaque table nourrissant l'API doit être peuplée (bloquant) ---
    for table in ("gold_volatility", "gold_sharpe", "gold_drawdown", "gold_correlation_matrix"):
        if gold.get(f"{table}_rows", 0) <= 0:
            errors.append(f"gold: {table} est vide")

    if gold.get("correlation_out_of_range", 0) > 0:
        errors.append(
            f"gold: {gold['correlation_out_of_range']} corrélation(s) hors [-1, 1]"
        )

    return errors, warnings
