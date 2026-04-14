"""
Correlation Calculator for Crypto Portfolio Diversification
Calculates correlation matrix to help build diversified portfolios.
"""

import os
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

    def get_price_series(
        self, coin_id: str, days: int = 30
    ) -> List[Tuple[datetime, float]]:
        """
        Get price time series for a cryptocurrency.

        Args:
            coin_id: Cryptocurrency identifier
            days: Number of days to look back

        Returns:
            List of (timestamp, price) tuples
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT timestamp, price_usd
            FROM crypto_prices
            WHERE coin_id = %s
              AND price_usd IS NOT NULL
              AND timestamp >= NOW() - INTERVAL '1 day' * %s
            ORDER BY timestamp ASC;
        """,
            (coin_id, days),
        )

        result = [
            (row["timestamp"], float(row["price_usd"])) for row in cursor.fetchall()
        ]
        cursor.close()

        return result

    def calculate_correlation(
        self, coin1: str, coin2: str, days: int = 30
    ) -> Optional[Dict]:
        """
        Calculate correlation between two cryptocurrencies.

        Args:
            coin1: First cryptocurrency
            coin2: Second cryptocurrency
            days: Analysis period

        Returns:
            Correlation metrics or None
        """
        self.connect()
        cursor = self.conn.cursor()

        # Get aligned price data for both coins
        # We need matching timestamps
        cursor.execute(
            """
            WITH coin1_data AS (
                SELECT
                    DATE_TRUNC('hour', timestamp) as time_bucket,
                    AVG(price_usd) as price
                FROM crypto_prices
                WHERE coin_id = %s
                  AND price_usd IS NOT NULL
                  AND timestamp >= NOW() - INTERVAL '1 day' * %s
                GROUP BY time_bucket
            ),
            coin2_data AS (
                SELECT
                    DATE_TRUNC('hour', timestamp) as time_bucket,
                    AVG(price_usd) as price
                FROM crypto_prices
                WHERE coin_id = %s
                  AND price_usd IS NOT NULL
                  AND timestamp >= NOW() - INTERVAL '1 day' * %s
                GROUP BY time_bucket
            )
            SELECT
                CORR(c1.price, c2.price) as correlation,
                COUNT(*) as sample_size,
                AVG(c1.price) as coin1_avg,
                AVG(c2.price) as coin2_avg,
                STDDEV(c1.price) as coin1_std,
                STDDEV(c2.price) as coin2_std
            FROM coin1_data c1
            INNER JOIN coin2_data c2 ON c1.time_bucket = c2.time_bucket;
        """,
            (coin1, days, coin2, days),
        )

        result = cursor.fetchone()
        cursor.close()

        if not result or result["sample_size"] < 2:
            return None

        correlation = float(result["correlation"]) if result["correlation"] else 0

        return {
            "coin1": coin1,
            "coin2": coin2,
            "correlation": correlation,
            "sample_size": result["sample_size"],
            "period_days": days,
            "strength": self._classify_correlation(correlation),
            "diversification_benefit": self._diversification_benefit(correlation),
        }

    def _classify_correlation(self, corr: float) -> str:
        """
        Classify correlation strength.

        Args:
            corr: Correlation coefficient (-1 to 1)

        Returns:
            Classification string
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
        if corr >= 0.8:
            return "❌ Poor - High correlation, low diversification"
        elif corr >= 0.5:
            return "⚠️  Moderate - Some diversification benefit"
        elif corr >= 0.2:
            return "✅ Good - Decent diversification"
        elif corr >= -0.2:
            return "🌟 Excellent - High diversification"
        else:
            return "🚀 Outstanding - Negative correlation, ideal hedge"

    def calculate_correlation_matrix(self, coin_ids: List[str], days: int = 30) -> Dict:
        """
        Calculate full correlation matrix for multiple cryptocurrencies.

        Args:
            coin_ids: List of cryptocurrency identifiers
            days: Analysis period

        Returns:
            Correlation matrix and statistics
        """
        correlation_matrix = {}
        correlations = []

        # Calculate all pairwise correlations
        for i, coin1 in enumerate(coin_ids):
            for j, coin2 in enumerate(coin_ids):
                if i < j:  # Only calculate unique pairs
                    result = self.calculate_correlation(coin1, coin2, days)
                    if result:
                        corr_value = result["correlation"]
                        # Store as tuple key for API
                        correlation_matrix[(coin1, coin2)] = corr_value
                        correlations.append(result)

        # Check if we have enough data
        if not correlations:
            return {
                "error": f"No correlation data available for the given coins over {days} days"
            }

        # Calculate average correlation (excluding self-correlation)
        valid_correlations = [
            c["correlation"] for c in correlations if c["correlation"] is not None
        ]

        avg_correlation = (
            sum(valid_correlations) / len(valid_correlations)
            if valid_correlations
            else 0
        )

        # Calculate diversification score (as float)
        diversification_score_info = self._calculate_diversification_score(
            avg_correlation
        )
        diversification_score = diversification_score_info["score"]

        return {
            "correlation_matrix": correlation_matrix,
            "period_days": days,
            "diversification_score": diversification_score,
        }

    def _calculate_diversification_score(self, avg_corr: float) -> Dict:
        """
        Calculate portfolio diversification score.

        Args:
            avg_corr: Average correlation across portfolio

        Returns:
            Diversification score and rating
        """
        # Diversification score: 0 (poor) to 100 (excellent)
        # Lower correlation = better diversification
        score = max(0, min(100, (1 - avg_corr) * 100))

        if score >= 80:
            rating = "🌟 Excellent"
        elif score >= 60:
            rating = "✅ Good"
        elif score >= 40:
            rating = "⚠️  Moderate"
        else:
            rating = "❌ Poor"

        return {
            "score": score,
            "rating": rating,
            "interpretation": f"Portfolio has {rating.split()[1].lower()} diversification",
        }

    def find_best_diversification_pairs(
        self, coin_ids: List[str], days: int = 30, top_n: int = 3
    ) -> List[Dict]:
        """
        Find the best crypto pairs for diversification.

        Args:
            coin_ids: List of cryptocurrencies
            days: Analysis period
            top_n: Number of top pairs to return

        Returns:
            Best pairs sorted by diversification benefit
        """
        correlations = []

        for i, coin1 in enumerate(coin_ids):
            for j, coin2 in enumerate(coin_ids):
                if i < j:  # Avoid duplicates
                    result = self.calculate_correlation(coin1, coin2, days)
                    if result:
                        correlations.append(result)

        # Sort by correlation (lowest = best diversification)
        correlations.sort(key=lambda x: abs(x["correlation"]))

        return correlations[:top_n]

    def find_worst_diversification_pairs(
        self, coin_ids: List[str], days: int = 30, top_n: int = 3
    ) -> List[Dict]:
        """
        Find crypto pairs with highest correlation (worst diversification).

        Args:
            coin_ids: List of cryptocurrencies
            days: Analysis period
            top_n: Number of pairs to return

        Returns:
            Worst pairs sorted by correlation
        """
        correlations = []

        for i, coin1 in enumerate(coin_ids):
            for j, coin2 in enumerate(coin_ids):
                if i < j:
                    result = self.calculate_correlation(coin1, coin2, days)
                    if result:
                        correlations.append(result)

        # Sort by correlation (highest = worst diversification)
        correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return correlations[:top_n]

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
