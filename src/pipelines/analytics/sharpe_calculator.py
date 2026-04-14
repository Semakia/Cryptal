"""
Sharpe Ratio Calculator for Crypto Investments
Calculates risk-adjusted returns to find the best investments.
"""
from typing import Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor


class SharpeCalculator:
    """
    Calculates Sharpe Ratio and risk-adjusted return metrics.

    Sharpe Ratio = (Return - Risk-Free Rate) / Volatility
    Higher is better: more return per unit of risk.
    """

    def __init__(self, db_config: Dict[str, str], risk_free_rate: float = 0.05):
        """
        Initialize calculator with database connection.

        Args:
            db_config: Database configuration dict
            risk_free_rate: Annual risk-free rate (default: 5% = 0.05)
        """
        self.db_config = db_config
        self.risk_free_rate = risk_free_rate
        self.conn = None

    def connect(self):
        """Establish database connection."""
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(
                host=self.db_config["host"],
                dbname=self.db_config["dbname"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                port=self.db_config.get("port", 5432),
                sslmode="require",
                cursor_factory=RealDictCursor,
            )

    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()

    def calculate_returns(self, coin_id: str, days: int = 30) -> Optional[Dict]:
        """
        Calculate return metrics for a cryptocurrency.

        Args:
            coin_id: Cryptocurrency identifier
            days: Analysis period

        Returns:
            Return metrics or None
        """
        self.connect()
        cursor = self.conn.cursor()

        # Get first and last prices
        cursor.execute(
            """
            WITH period_prices AS (
                SELECT price_usd, timestamp
                FROM crypto_prices
                WHERE coin_id = %s
                  AND price_usd IS NOT NULL
                  AND timestamp >= NOW() - INTERVAL '1 day' * %s
                ORDER BY timestamp ASC
            ),
            first_price AS (
                SELECT price_usd, timestamp
                FROM period_prices
                LIMIT 1
            ),
            last_price AS (
                SELECT price_usd, timestamp
                FROM period_prices
                ORDER BY timestamp DESC
                LIMIT 1
            )
            SELECT
                f.price_usd as first_price,
                f.timestamp as first_date,
                l.price_usd as last_price,
                l.timestamp as last_date,
                EXTRACT(EPOCH FROM (l.timestamp - f.timestamp)) / 86400 as actual_days,
                (SELECT COUNT(*) FROM period_prices) as data_points
            FROM first_price f, last_price l;
        """,
            (coin_id, days),
        )

        result = cursor.fetchone()
        cursor.close()

        if not result or result["actual_days"] == 0:
            return None

        # Check minimum period for calculations (minimum 1 day)
        actual_days = float(result["actual_days"])
        if actual_days < 1:
            return None

        first_price = float(result["first_price"])
        last_price = float(result["last_price"])

        # Calculate returns
        absolute_return = last_price - first_price
        percentage_return = (absolute_return / first_price) * 100

        # For reference: annualized return (hypothetical if trend continues)
        # WARNING: This assumes the trend will repeat, which is unrealistic for short periods
        annualized_return = (
            ((last_price / first_price) ** (365 / actual_days) - 1) * 100
            if actual_days > 0
            else 0
        )

        return {
            "coin_id": coin_id,
            "start_price": first_price,
            "end_price": last_price,
            "first_date": result["first_date"],
            "last_date": result["last_date"],
            "period_days": int(actual_days),
            "data_points": result["data_points"],
            "absolute_return": absolute_return,
            "total_return": percentage_return,  # This is the ACTUAL return over the period
            "annualized_return": annualized_return,  # Hypothetical only - don't use for Sharpe!
        }

    def calculate_volatility(self, coin_id: str, days: int = 30) -> Optional[float]:
        """
        Calculate annualized volatility (standard deviation).

        Args:
            coin_id: Cryptocurrency identifier
            days: Analysis period

        Returns:
            Annualized volatility (%) or None
        """
        self.connect()
        cursor = self.conn.cursor()

        # Determine aggregation period based on analysis window
        if days >= 14:
            time_bucket_sql = "date_trunc('day', timestamp)"
            periods_per_year = 365
        elif days >= 3:
            time_bucket_sql = "date_trunc('hour', timestamp)"
            periods_per_year = 365 * 24
        else:
            time_bucket_sql = "date_trunc('hour', timestamp)"
            periods_per_year = 365 * 24

        # Calculate returns and their standard deviation with proper time aggregation
        query = f"""
            WITH aggregated_prices AS (
                SELECT
                    {time_bucket_sql} as time_bucket,
                    AVG(price_usd) as avg_price
                FROM crypto_prices
                WHERE coin_id = %s
                  AND price_usd IS NOT NULL
                  AND timestamp >= NOW() - INTERVAL '1 day' * %s
                GROUP BY {time_bucket_sql}
                ORDER BY time_bucket
            ),
            price_series AS (
                SELECT
                    avg_price as price_usd,
                    LAG(avg_price) OVER (ORDER BY time_bucket) as prev_price
                FROM aggregated_prices
            ),
            returns AS (
                SELECT
                    ((price_usd - prev_price) / prev_price) * 100 as return_pct
                FROM price_series
                WHERE prev_price IS NOT NULL
            )
            SELECT
                STDDEV(return_pct) as std_volatility,
                COUNT(*) as sample_size
            FROM returns;
        """

        cursor.execute(query, (coin_id, days))

        result = cursor.fetchone()
        cursor.close()

        if not result or result["sample_size"] < 2:
            return None

        std_volatility = (
            float(result["std_volatility"]) if result["std_volatility"] else 0
        )

        # Annualize volatility using the appropriate factor for our aggregation period
        annualized_volatility = std_volatility * (periods_per_year**0.5)

        return annualized_volatility

    def calculate_sharpe_ratio(
        self, coin_id: str, days: int = 30, risk_free_rate: float = None
    ) -> Optional[Dict]:
        """
        Calculate Sharpe Ratio for a cryptocurrency.

        Args:
            coin_id: Cryptocurrency identifier
            days: Analysis period
            risk_free_rate: Annual risk-free rate (overrides default if provided)

        Returns:
            Sharpe ratio and related metrics or None
        """
        # Use provided risk_free_rate or default
        rfr = risk_free_rate if risk_free_rate is not None else self.risk_free_rate

        # Get returns
        returns = self.calculate_returns(coin_id, days)
        if not returns:
            return {"error": f"No return data available for {coin_id} over {days} days"}

        # Check minimum period for reliable annualization
        if returns["period_days"] < 5:
            return {
                "error": f"Insufficient data period for {coin_id}: {returns['period_days']} days (minimum 5 days required)"
            }

        # Get volatility
        volatility = self.calculate_volatility(coin_id, days)
        if volatility is None or volatility == 0:
            return {
                "error": f"No volatility data available for {coin_id} over {days} days"
            }

        # Calculate Sharpe Ratio using ACTUAL returns (not annualized)
        # This is more honest for short periods and doesn't assume trends will repeat
        #
        # Traditional formula: (Annualized_Return - Risk_Free_Rate) / Annualized_Volatility
        # Our improved formula: (Actual_Return - Adjusted_Risk_Free) / Period_Volatility
        # Then we scale back to annualized basis for comparison

        # Adjust risk-free rate to the actual period
        period_risk_free = rfr * (returns["period_days"] / 365)

        # Calculate excess return over risk-free rate for the period
        excess_return = returns["total_return"] - (period_risk_free * 100)

        # Period volatility (de-annualize)
        period_volatility = volatility / ((365 / returns["period_days"]) ** 0.5)

        # Sharpe ratio for the period
        sharpe_ratio = excess_return / period_volatility if period_volatility > 0 else 0

        return {
            "coin_id": returns["coin_id"],
            "period_days": returns["period_days"],
            "data_points": returns["data_points"],
            "total_return": returns[
                "total_return"
            ],  # Actual return (e.g., -9% over 30 days)
            "annualized_return": returns[
                "annualized_return"
            ],  # Hypothetical (if trend continues)
            "annualized_volatility": volatility,
            "sharpe_ratio": sharpe_ratio,  # Based on actual returns, not hypothetical
            "start_price": returns["start_price"],
            "end_price": returns["end_price"],
        }

    def _classify_sharpe(self, sharpe: float) -> str:
        """
        Classify Sharpe Ratio quality.

        Args:
            sharpe: Sharpe ratio value

        Returns:
            Classification string
        """
        if sharpe >= 3:
            return "🌟 Exceptional"
        elif sharpe >= 2:
            return "🚀 Excellent"
        elif sharpe >= 1:
            return "✅ Good"
        elif sharpe >= 0:
            return "⚠️  Acceptable"
        else:
            return "❌ Poor (Negative)"

    def compare_sharpe_ratios(self, coin_ids: List[str], days: int = 30) -> List[Dict]:
        """
        Compare Sharpe Ratios across multiple cryptocurrencies.

        Args:
            coin_ids: List of cryptocurrency identifiers
            days: Analysis period

        Returns:
            List of Sharpe ratios, sorted best to worst
        """
        results = []

        for coin_id in coin_ids:
            sharpe = self.calculate_sharpe_ratio(coin_id, days)
            if sharpe:
                results.append(sharpe)

        # Sort by Sharpe ratio (highest = best)
        results.sort(key=lambda x: x["sharpe_ratio"], reverse=True)

        return results

    def find_best_risk_adjusted_investment(
        self, coin_ids: List[str], days: int = 30
    ) -> Optional[Dict]:
        """
        Find the cryptocurrency with the best risk-adjusted return.

        Args:
            coin_ids: List of cryptocurrencies to compare
            days: Analysis period

        Returns:
            Best investment based on Sharpe ratio
        """
        results = self.compare_sharpe_ratios(coin_ids, days)

        if not results:
            return None

        best = results[0]

        return {
            **best,
            "ranking": 1,
            "total_compared": len(results),
            "better_than_pct": 100.0,
        }

    def get_available_coins(self) -> List[str]:
        """Get list of available cryptocurrencies."""
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT DISTINCT coin_id
            FROM crypto_prices
            WHERE price_usd IS NOT NULL
            ORDER BY coin_id;
        """
        )

        coins = [row["coin_id"] for row in cursor.fetchall()]
        cursor.close()

        return coins
