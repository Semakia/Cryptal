from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor


class VolatilityCalculator:
    """
    Calculates volatility metrics for cryptocurrencies.

    Metrics:
    - Standard deviation (volatility)
    - Mean price
    - Price range (min/max)
    """

    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize calculator with database connection.

        Args:
            db_config: Database configuration dict
        """
        self.db_config = db_config
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

    def calculate_volatility(self, coin_id: str, days: int = 30) -> Optional[Dict]:
        """
        Calculate volatility metrics for a cryptocurrency.

        Args:
            coin_id: Cryptocurrency identifier
            days: Number of days to look back (default: 30)

        Returns:
            Dictionary with volatility metrics or None
        """
        self.connect()
        cursor = self.conn.cursor()

        # Determine aggregation period based on analysis window
        # For 30-day analysis: use daily aggregation (more stable)
        # For 7-day analysis: use hourly aggregation (6h had issues)
        # For 24h analysis: use hourly aggregation
        if days >= 14:
            time_bucket_sql = "date_trunc('day', timestamp)"
            periods_per_year = 365
        elif days >= 3:
            time_bucket_sql = "date_trunc('hour', timestamp)"
            periods_per_year = 365 * 24  # hourly
        else:
            time_bucket_sql = "date_trunc('hour', timestamp)"
            periods_per_year = 365 * 24

        # Calculate statistics using returns (proper financial volatility)
        # IMPORTANT: Aggregate to appropriate time buckets BEFORE calculating returns
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
                    time_bucket,
                    avg_price as price_usd,
                    LAG(avg_price) OVER (ORDER BY time_bucket) as prev_price
                FROM aggregated_prices
            ),
            returns AS (
                SELECT
                    time_bucket,
                    price_usd,
                    prev_price,
                    CASE
                        WHEN prev_price > 0 THEN ((price_usd - prev_price) / prev_price) * 100
                        ELSE NULL
                    END as return_pct
                FROM price_series
                WHERE prev_price IS NOT NULL
            ),
            return_stats AS (
                SELECT
                    COUNT(*) as sample_size,
                    AVG(return_pct) as mean_return,
                    STDDEV_POP(return_pct) as std_dev_returns,
                    VARIANCE(return_pct) as variance_returns
                FROM returns
                WHERE return_pct IS NOT NULL
            ),
            price_stats AS (
                SELECT
                    MIN(avg_price) as min_price,
                    MAX(avg_price) as max_price,
                    AVG(avg_price) as mean_price
                FROM aggregated_prices
            )
            SELECT
                r.sample_size,
                r.mean_return,
                r.std_dev_returns,
                r.variance_returns,
                p.min_price,
                p.max_price,
                p.mean_price
            FROM return_stats r, price_stats p;
        """

        cursor.execute(query, (coin_id, days))

        result = cursor.fetchone()
        cursor.close()

        if not result or result["sample_size"] == 0:
            return None

        mean_price = float(result["mean_price"])
        std_dev_returns = (
            float(result["std_dev_returns"]) if result["std_dev_returns"] else 0
        )
        min_price = float(result["min_price"])
        max_price = float(result["max_price"])

        # Annualize volatility using the appropriate factor for our aggregation period
        # This matches the time_bucket determined above
        annualized_volatility = std_dev_returns * (periods_per_year**0.5)

        # Period volatility (actual volatility for the time period, not annualized)
        period_volatility = std_dev_returns

        # Calculate price range (absolute difference)
        price_range = max_price - min_price

        return {
            "coin_id": coin_id,
            "period_days": days,
            "data_points": result["sample_size"],
            "mean_price": mean_price,
            "period_volatility": period_volatility,  # Actual volatility for the period (%)
            "annualized_volatility": annualized_volatility,  # Annualized volatility (%)
            "min_price": min_price,
            "max_price": max_price,
            "price_range": price_range,
        }

    def compare_volatility(self, coin_ids: List[str], days: int = 30) -> List[Dict]:
        """
        Compare volatility across multiple cryptocurrencies.

        Args:
            coin_ids: List of cryptocurrency identifiers
            days: Number of days to analyze

        Returns:
            List of volatility metrics, sorted by risk (low to high)
        """
        results = []

        for coin_id in coin_ids:
            vol = self.calculate_volatility(coin_id, days)
            if vol:
                results.append(vol)

        # Sort by annualized volatility (low to high = less risky to more risky)
        results.sort(key=lambda x: x["annualized_volatility"])

        return results

    def get_risk_adjusted_returns(
        self, coin_id: str, investment_amount: float, days: int = 30
    ) -> Optional[Dict]:
        """
        Calculate risk-adjusted return metrics.

        Args:
            coin_id: Cryptocurrency identifier
            investment_amount: Amount to invest
            days: Analysis period

        Returns:
            Risk-adjusted metrics
        """
        vol = self.calculate_volatility(coin_id, days)
        if not vol:
            return None

        self.connect()
        cursor = self.conn.cursor()

        # Get first and last prices for return calculation
        cursor.execute(
            """
            SELECT price_usd, timestamp
            FROM crypto_prices
            WHERE coin_id = %s
              AND price_usd IS NOT NULL
              AND timestamp >= NOW() - INTERVAL '1 day' * %s
            ORDER BY timestamp ASC
            LIMIT 1;
        """,
            (coin_id, days),
        )
        first = cursor.fetchone()

        cursor.execute(
            """
            SELECT price_usd, timestamp
            FROM crypto_prices
            WHERE coin_id = %s
              AND price_usd IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 1;
        """,
            (coin_id,),
        )
        last = cursor.fetchone()

        cursor.close()

        if not first or not last:
            return vol

        # Calculate returns
        first_price = float(first["price_usd"])
        last_price = float(last["price_usd"])
        total_return = ((last_price - first_price) / first_price) * 100

        return {
            **vol,
            "first_price": first_price,
            "last_price": last_price,
            "total_return_pct": total_return,
            "investment_amount": investment_amount,
            "current_value": investment_amount * (1 + total_return / 100),
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
