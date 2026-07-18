"""
Correlation Calculator for Crypto Portfolio Diversification
Calculates correlation matrix to help build diversified portfolios.
Source: crypto_prices_series table (Silver layer)
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor


class CorrelationCalculator:
    """
    Calculates correlation between cryptocurrencies for portfolio diversification.

    Features:
    - Pairwise correlation between cryptos
    - Full correlation matrix
    - Diversification score
    - Portfolio recommendations

    """

    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize calculator with database connection.

        Args:
            db_config: Database configuration dict (SILVER_DB_*)
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
            )

    def get_price_history(self, coin_id: str, start_date: str = None,
                          end_date: str = None, days: int = None) -> List[Dict]:
        """
        Fetch hourly price history for a cryptocurrency from
         crypto_prices_series.

        Args:
            coin_id: Cryptocurrency identifier
            start_date: Start date in 'YYYY-MM-DD' format (optional)
            end_date: End date in 'YYYY-MM-DD' format (optional)
            days: Lookback window in days (optional). Takes precedence over
                  start_date when provided.

        Returns:
            List of dicts with price history data
        """
        self.connect()
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        conditions = ["coin_id = %s"]
        params = [coin_id]

        if days is not None:
            conditions.append("time_bucket >= NOW() - INTERVAL '1 day' * %s")
            params.append(days)
        elif start_date:
            conditions.append("time_bucket >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("time_bucket <= %s")
            params.append(end_date)

        query = f"""
            SELECT time_bucket, price_usd
            FROM crypto_prices_series
            WHERE {' AND '.join(conditions)}
            ORDER BY time_bucket ASC
        """

        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        cursor.close()

        return [dict(row) for row in results]

    def get_returns_series(self, prices: List[float]) -> List[float]:
        """
        Calculate returns series from price series.

        Args:
            prices: List of prices in chronological order

        Returns:
            List of percentage returns
        """
        if len(prices) < 2:
            return []

        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1] * 100
            returns.append(ret)

        return returns

    def calculate_correlation(self, coin1: str, coin2: str,
                              start_date: str = None,
                              end_date: str = None) -> Dict:
        """
        Calculate correlation between two cryptocurrencies.

        Args:
            coin1: First cryptocurrency identifier
            coin2: Second cryptocurrency identifier
            start_date: Start date in 'YYYY-MM-DD' format (optional)
            end_date: End date in 'YYYY-MM-DD' format (optional)

        Returns:
            Dict with correlation metrics
        """
        prices1_data = self.get_price_history(coin1, start_date, end_date)
        prices2_data = self.get_price_history(coin2, start_date, end_date)

        if not prices1_data or not prices2_data:
            return {"error": "No price data found", "coin1": coin1, "coin2": coin2}

        # Align by timestamp
        prices1 = {row["time_bucket"]: row["price_usd"] for row in prices1_data}
        prices2 = {row["time_bucket"]: row["price_usd"] for row in prices2_data}

        common_timestamps = sorted(set(prices1.keys()) & set(prices2.keys()))

        if len(common_timestamps) < 10:
            return {
                "error": "Not enough common data points",
                "coin1": coin1,
                "coin2": coin2,
                "common_points": len(common_timestamps)
            }

        prices1_aligned = [prices1[ts] for ts in common_timestamps]
        prices2_aligned = [prices2[ts] for ts in common_timestamps]

        returns1 = self.get_returns_series(prices1_aligned)
        returns2 = self.get_returns_series(prices2_aligned)

        if not returns1 or not returns2:
            return {"error": "Not enough data for returns calculation"}

        # Calculate Pearson correlation
        n = len(returns1)
        mean1 = sum(returns1) / n
        mean2 = sum(returns2) / n

        numerator = sum((r1 - mean1) * (r2 - mean2) for r1, r2 in zip(returns1, returns2))
        denom1 = sum((r - mean1) ** 2 for r in returns1) ** 0.5
        denom2 = sum((r - mean2) ** 2 for r in returns2) ** 0.5

        if denom1 == 0 or denom2 == 0:
            correlation = 0
        else:
            correlation = numerator / (denom1 * denom2)

        return {
            "coin1": coin1,
            "coin2": coin2,
            "correlation": round(correlation, 4),
            "common_data_points": len(common_timestamps),
            "start_date": common_timestamps[0].strftime("%Y-%m-%d %H:%M:%S") if common_timestamps else None,
            "end_date": common_timestamps[-1].strftime("%Y-%m-%d %H:%M:%S") if common_timestamps else None,
            "interpretation": self._interpret_correlation(correlation)
        }

    def _interpret_correlation(self, corr: float) -> str:
        """
        Interpret correlation coefficient.

        Args:
            corr: Correlation coefficient (-1 to 1)

        Returns:
            String interpretation
        """
        abs_corr = abs(corr)
        if abs_corr >= 0.9:
            return "Very Strong"
        elif abs_corr >= 0.7:
            return "Strong"
        elif abs_corr >= 0.4:
            return "Moderate"
        elif abs_corr >= 0.2:
            return "Weak"
        else:
            return "Very Weak / None"

    def _diversification_benefit(self, corr: float) -> str:
        """
        Assess diversification benefit based on correlation.

        Args:
            corr: Correlation coefficient

        Returns:
            Diversification assessment
        """
        if corr <= -0.5:
            return "Excellent - Strong negative correlation provides excellent diversification"
        elif corr <= 0:
            return "Good - Low or negative correlation provides good diversification"
        elif corr <= 0.3:
            return "Moderate - Some diversification benefit"
        elif corr <= 0.6:
            return "Limited - High correlation reduces diversification benefit"
        else:
            return "Poor - Very high correlation provides little diversification"

    @staticmethod
    def _pearson(returns1: List[float], returns2: List[float]) -> float:
        """Pearson correlation between two equal-length return series."""
        n = min(len(returns1), len(returns2))
        if n < 2:
            return 0.0
        r1, r2 = returns1[:n], returns2[:n]
        mean1 = sum(r1) / n
        mean2 = sum(r2) / n
        numerator = sum((a - mean1) * (b - mean2) for a, b in zip(r1, r2))
        denom1 = sum((a - mean1) ** 2 for a in r1) ** 0.5
        denom2 = sum((b - mean2) ** 2 for b in r2) ** 0.5
        if denom1 == 0 or denom2 == 0:
            return 0.0
        return numerator / (denom1 * denom2)

    def calculate_correlation_matrix(self, coin_ids: List[str] = None,
                                      days: int = 30) -> Dict:
        """
        Calculate the correlation matrix for a list of cryptocurrencies.

        Args:
            coin_ids: List of cryptocurrency identifiers (optional)
            days: Lookback window in days (default: 30)

        Returns:
            Dict consumed by the /metrics/correlation endpoint:
            - period_days: lookback window
            - correlation_matrix: flat dict keyed by (coin_1, coin_2) tuples
              (unique unordered pairs) -> Pearson correlation
            - diversification_score, avg_correlation, coins_analyzed, data_points
        """
        if coin_ids is None:
            coin_ids = self.get_available_coins()[:10]  # Limit to 10

        if len(coin_ids) < 2:
            return {"error": "Need at least 2 coins for correlation matrix"}

        # Fetch all price data over the lookback window
        all_prices = {}
        for coin in coin_ids:
            data = self.get_price_history(coin, days=days)
            if data:
                all_prices[coin] = {
                    row["time_bucket"]: row["price_usd"] for row in data
                }

        coins = [c for c in coin_ids if c in all_prices]
        if len(coins) < 2:
            return {"error": "Not enough coins with data for correlation matrix"}

        # Align on common timestamps
        common_timestamps = sorted(
            set.intersection(*[set(all_prices[c].keys()) for c in coins])
        )
        if len(common_timestamps) < 10:
            return {"error": "Not enough common data points across all coins"}

        # Pairwise correlations on unique unordered pairs
        correlation_matrix = {}
        all_corrs = []
        for i, coin1 in enumerate(coins):
            for coin2 in coins[i + 1:]:
                prices1 = [all_prices[coin1][ts] for ts in common_timestamps]
                prices2 = [all_prices[coin2][ts] for ts in common_timestamps]
                corr = round(
                    self._pearson(
                        self.get_returns_series(prices1),
                        self.get_returns_series(prices2),
                    ),
                    4,
                )
                correlation_matrix[(coin1, coin2)] = corr
                all_corrs.append(corr)

        avg_correlation = sum(all_corrs) / len(all_corrs) if all_corrs else 0

        return {
            "period_days": days,
            "correlation_matrix": correlation_matrix,
            "avg_correlation": round(avg_correlation, 4),
            "diversification_score": round((1 - avg_correlation) * 100, 2),
            "coins_analyzed": coins,
            "data_points": len(common_timestamps),
        }

    def get_available_coins(self) -> List[str]:
        """
        Get list of available cryptocurrencies from crypto_prices_series.

        Returns:
            List of coin identifiers
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT DISTINCT coin_id
            FROM crypto_prices_series
            WHERE price_usd IS NOT NULL
            ORDER BY coin_id;
            """
        )

        coins = [row["coin_id"] for row in cursor.fetchall()]
        cursor.close()

        return coins