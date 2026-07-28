"""Gate qualité du DAG : contrôle les couches silver & gold, sort en erreur si
un contrôle bloquant échoue.

Lancé par le task Airflow `data_quality_check` (BashOperator), après build_gold.

Config lue depuis l'environnement :
    SILVER_DB_* / GOLD_DB_*      : connexions
    QUALITY_MIN_COINS            : nb minimal de cryptos en silver (défaut 3)
    QUALITY_MAX_STALENESS_DAYS   : seuil de fraîcheur silver, en jours (défaut 400)
"""

import os
import sys

import psycopg2

from pipelines.quality.checks import (
    evaluate_metrics,
    gather_gold_metrics,
    gather_silver_metrics,
)


def _db_config(prefix: str) -> dict:
    return {
        "host": os.environ[f"{prefix}_DB_HOST"],
        "dbname": os.environ[f"{prefix}_DB_NAME"],
        "user": os.environ[f"{prefix}_DB_USER"],
        "password": os.environ[f"{prefix}_DB_PASSWORD"],
        "port": os.getenv(f"{prefix}_DB_PORT", "5432"),
    }


def main() -> int:
    min_coins = int(os.getenv("QUALITY_MIN_COINS", "3"))
    max_staleness = float(os.getenv("QUALITY_MAX_STALENESS_DAYS", "400"))

    silver_conn = psycopg2.connect(**_db_config("SILVER"))
    gold_conn = psycopg2.connect(**_db_config("GOLD"))
    try:
        silver = gather_silver_metrics(silver_conn)
        gold = gather_gold_metrics(gold_conn)
    finally:
        silver_conn.close()
        gold_conn.close()

    errors, warnings = evaluate_metrics(
        silver, gold, min_coins=min_coins, max_staleness_days=max_staleness
    )

    print("=" * 60)
    print("RAPPORT QUALITÉ DE DONNÉES")
    print("=" * 60)
    print("Silver :", silver)
    print("Gold   :", gold)
    for w in warnings:
        print(f"  [WARN]  {w}")
    for e in errors:
        print(f"  [ERROR] {e}")
    print("=" * 60)

    if errors:
        print(f"ÉCHEC : {len(errors)} contrôle(s) bloquant(s), {len(warnings)} avertissement(s).")
        return 1
    print(f"OK : 0 erreur, {len(warnings)} avertissement(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
