"""
Build de la couche GOLD (métriques pré-calculées qui nourrissent l'API).

Réutilise les calculateurs existants (lecture SILVER crypto_prices_series) et
matérialise les résultats dans crypto_viz_gold :
    - gold_volatility          (1 ligne / coin)
    - gold_sharpe              (1 ligne / coin)
    - gold_drawdown            (1 ligne / coin)
    - gold_correlation_matrix  (1 ligne / paire)

Config lue depuis l'environnement :
    SILVER_DB_* : source des calculateurs
    GOLD_DB_*   : destination
    GOLD_PERIOD_DAYS : fenêtre d'analyse (défaut 30 ; 365 pour la donnée démo)
    RISK_FREE_RATE   : taux sans risque pour le Sharpe (défaut 0.02)
"""
import os

import psycopg2

from pipelines.transform.volatility_calculator import VolatilityCalculator
from pipelines.transform.sharpe_calculator import SharpeCalculator
from pipelines.transform.drawdown_calculator import DrawdownCalculator
from pipelines.transform.correlation_calculator import CorrelationCalculator


def _db_config(prefix: str) -> dict:
    return {
        "host": os.environ[f"{prefix}_DB_HOST"],
        "dbname": os.environ[f"{prefix}_DB_NAME"],
        "user": os.environ[f"{prefix}_DB_USER"],
        "password": os.environ[f"{prefix}_DB_PASSWORD"],
        "port": os.getenv(f"{prefix}_DB_PORT", "5432"),
    }


DDL = """
CREATE TABLE IF NOT EXISTS gold_volatility (
    coin_id               TEXT PRIMARY KEY,
    period_days           INTEGER,
    data_points           INTEGER,
    mean_price            DOUBLE PRECISION,
    period_volatility     DOUBLE PRECISION,
    annualized_volatility DOUBLE PRECISION,
    computed_at           TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS gold_sharpe (
    coin_id               TEXT PRIMARY KEY,
    period_days           INTEGER,
    data_points           INTEGER,
    total_return          DOUBLE PRECISION,
    annualized_return     DOUBLE PRECISION,
    annualized_volatility DOUBLE PRECISION,
    sharpe_ratio          DOUBLE PRECISION,
    start_price           DOUBLE PRECISION,
    end_price             DOUBLE PRECISION,
    computed_at           TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS gold_drawdown (
    coin_id          TEXT PRIMARY KEY,
    period_days      INTEGER,
    data_points      INTEGER,
    max_drawdown_pct DOUBLE PRECISION,
    peak_price       DOUBLE PRECISION,
    trough_price     DOUBLE PRECISION,
    peak_date        TIMESTAMP,
    trough_date      TIMESTAMP,
    computed_at      TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS gold_correlation_matrix (
    crypto_1    TEXT,
    crypto_2    TEXT,
    correlation DOUBLE PRECISION,
    period_days INTEGER,
    computed_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (crypto_1, crypto_2)
);
"""


def _ok(result) -> bool:
    """Un résultat de calculateur est exploitable s'il n'est ni None ni {error}."""
    return bool(result) and "error" not in result


def main():
    period = int(os.getenv("GOLD_PERIOD_DAYS", "30"))
    rfr = float(os.getenv("RISK_FREE_RATE", "0.02"))

    silver = _db_config("SILVER")
    gold = _db_config("GOLD")

    vol_calc = VolatilityCalculator(silver)
    sharpe_calc = SharpeCalculator(silver)
    dd_calc = DrawdownCalculator(silver)
    corr_calc = CorrelationCalculator(silver)

    gold_conn = psycopg2.connect(
        host=gold["host"], dbname=gold["dbname"], user=gold["user"],
        password=gold["password"], port=gold["port"], sslmode="require",
    )
    gold_conn.autocommit = False
    cur = gold_conn.cursor()

    # Schéma (idempotent)
    cur.execute(DDL)
    gold_conn.commit()

    coins = vol_calc.get_available_coins()
    print(f"[gold] {len(coins)} coins, fenêtre={period} jours : {coins}")

    n_vol = n_sharpe = n_dd = 0
    for coin in coins:
        vol = vol_calc.calculate_volatility(coin, days=period)
        if _ok(vol):
            cur.execute(
                """
                INSERT INTO gold_volatility (coin_id, period_days, data_points,
                    mean_price, period_volatility, annualized_volatility,
                    computed_at)
                VALUES (%s,%s,%s,%s,%s,%s, NOW())
                ON CONFLICT (coin_id) DO UPDATE SET
                    period_days=EXCLUDED.period_days,
                    data_points=EXCLUDED.data_points,
                    mean_price=EXCLUDED.mean_price,
                    period_volatility=EXCLUDED.period_volatility,
                    annualized_volatility=EXCLUDED.annualized_volatility,
                    computed_at=NOW();
                """,
                (coin, vol["period_days"], vol["data_points"],
                 vol["mean_price"], vol["period_volatility"],
                 vol["annualized_volatility"]),
            )
            n_vol += 1

        sharpe = sharpe_calc.calculate_sharpe_ratio(
            coin, days=period, risk_free_rate=rfr
        )
        if _ok(sharpe):
            cur.execute(
                """
                INSERT INTO gold_sharpe (coin_id, period_days, data_points,
                    total_return, annualized_return, annualized_volatility,
                    sharpe_ratio, start_price, end_price, computed_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s, NOW())
                ON CONFLICT (coin_id) DO UPDATE SET
                    period_days=EXCLUDED.period_days,
                    data_points=EXCLUDED.data_points,
                    total_return=EXCLUDED.total_return,
                    annualized_return=EXCLUDED.annualized_return,
                    annualized_volatility=EXCLUDED.annualized_volatility,
                    sharpe_ratio=EXCLUDED.sharpe_ratio,
                    start_price=EXCLUDED.start_price,
                    end_price=EXCLUDED.end_price,
                    computed_at=NOW();
                """,
                (coin, sharpe["period_days"], sharpe["data_points"],
                 sharpe["total_return"], sharpe["annualized_return"],
                 sharpe["annualized_volatility"], sharpe["sharpe_ratio"],
                 sharpe["start_price"], sharpe["end_price"]),
            )
            n_sharpe += 1

        dd = dd_calc.calculate_max_drawdown(coin, days=period)
        if _ok(dd):
            cur.execute(
                """
                INSERT INTO gold_drawdown (coin_id, period_days, data_points,
                    max_drawdown_pct, peak_price, trough_price, peak_date,
                    trough_date, computed_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s, NOW())
                ON CONFLICT (coin_id) DO UPDATE SET
                    period_days=EXCLUDED.period_days,
                    data_points=EXCLUDED.data_points,
                    max_drawdown_pct=EXCLUDED.max_drawdown_pct,
                    peak_price=EXCLUDED.peak_price,
                    trough_price=EXCLUDED.trough_price,
                    peak_date=EXCLUDED.peak_date,
                    trough_date=EXCLUDED.trough_date,
                    computed_at=NOW();
                """,
                (coin, dd["period_days"], dd["data_points"],
                 dd["max_drawdown_pct"], dd["peak_price"], dd["trough_price"],
                 dd["peak_date"], dd["trough_date"]),
            )
            n_dd += 1

    # Matrice de corrélation : recalcul complet -> on remplace la table
    corr = corr_calc.calculate_correlation_matrix(days=period)
    n_pairs = 0
    if _ok(corr):
        cur.execute("TRUNCATE gold_correlation_matrix;")
        for (c1, c2), value in corr["correlation_matrix"].items():
            cur.execute(
                """
                INSERT INTO gold_correlation_matrix
                    (crypto_1, crypto_2, correlation, period_days, computed_at)
                VALUES (%s,%s,%s,%s, NOW());
                """,
                (c1, c2, value, corr["period_days"]),
            )
            n_pairs += 1
    else:
        print(f"[gold] corrélation non calculée : {corr}")

    gold_conn.commit()
    cur.close()
    gold_conn.close()
    vol_calc.close()
    sharpe_calc.close()
    dd_calc.close()
    corr_calc.close()

    print(
        f"[gold] écrit -> volatility={n_vol}, sharpe={n_sharpe}, "
        f"drawdown={n_dd}, correlation_pairs={n_pairs}"
    )


if __name__ == "__main__":
    main()
