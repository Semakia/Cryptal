"""
Drawdown Calculator for Crypto Investments
Calculates maximum drawdown and recovery metrics.
Source: crypto_prices_series table (Silver layer)
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor


class DrawdownCalculator:
    """
    Calculates drawdown metrics to measure downside risk.

    Metrics:
    - Maximum drawdown (worst loss from peak)
    - Current drawdown
    - Recovery time
    - Peak and trough information
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

    def get_price_history(
        self,
        coin_id: str,
        start_date: str = None
    ) -> List[Dict]:
        """
        Fetch hourly price history for a cryptocurrency
         from crypto_prices_series.

        Args:
            coin_id: Cryptocurrency identifier (e.g., 'bitcoin', 'ethereum')
            start_date: Start date in 'YYYY-MM-DD' format (optional)

        Returns:
            List of dicts with price history data
        """
        self.connect()
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        if start_date:
            query = """
                SELECT time_bucket, price_usd
                FROM crypto_prices_series
                WHERE coin_id = %s AND time_bucket >= %s
                ORDER BY time_bucket ASC
            """
            cursor.execute(query, (coin_id, start_date))
        else:
            query = """
                SELECT time_bucket, price_usd
                FROM crypto_prices_series
                WHERE coin_id = %s
                ORDER BY time_bucket ASC
            """
            cursor.execute(query, (coin_id,))

        results = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in results]

    def calculate_drawdown_series(self, prices: List[float]) -> List[float]:
        """
        Calculate drawdown series from a list of prices.

        Args:
            prices: List of prices in chronological order

        Returns:
            List of drawdown percentages at each point
        """
        if not prices:
            return []

        drawdowns = []
        peak = prices[0]

        for price in prices:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak * 100 if peak > 0 else 0
            drawdowns.append(drawdown)

        return drawdowns

    def calculate_max_drawdown(
        self,
        coin_id: str,
        days: int = 30
    ) -> Dict:
        """
        Calculate maximum drawdown for a cryptocurrency over a lookback period.

        Args:
            coin_id: Cryptocurrency identifier
            days: Number of days to look back (default: 30)

        Returns:
            Dict aligned with the API DrawdownMetrics model:
            coin_id, period_days, data_points, max_drawdown_pct,
            max_drawdown_value, peak_price, trough_price, peak_date, trough_date.
        """
        self.connect()
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT time_bucket, price_usd
            FROM crypto_prices_series
            WHERE coin_id = %s
              AND price_usd IS NOT NULL
              AND time_bucket >= NOW() - INTERVAL '1 day' * %s
            ORDER BY time_bucket ASC
            """,
            (coin_id, days),
        )
        history = cursor.fetchall()
        cursor.close()

        if not history or len(history) < 2:
            return {"error": f"No price data found for {coin_id}", "coin_id": coin_id}

        prices = [float(row["price_usd"]) for row in history]
        timestamps = [row["time_bucket"] for row in history]

        # Track the running peak and the deepest decline from any peak.
        running_peak = prices[0]
        running_peak_idx = 0
        max_dd_pct = 0.0
        peak_price = prices[0]
        peak_idx = 0
        trough_price = prices[0]
        trough_idx = 0

        for i, price in enumerate(prices):
            if price > running_peak:
                running_peak = price
                running_peak_idx = i
            drawdown = (
                (running_peak - price) / running_peak * 100
                if running_peak > 0
                else 0.0
            )
            if drawdown > max_dd_pct:
                max_dd_pct = drawdown
                peak_price = running_peak
                peak_idx = running_peak_idx
                trough_price = price
                trough_idx = i

        return {
            "coin_id": coin_id,
            "period_days": days,
            "data_points": len(prices),
            "max_drawdown_pct": round(max_dd_pct, 2),
            "max_drawdown_value": round(peak_price - trough_price, 2),
            "peak_price": round(peak_price, 2),
            "trough_price": round(trough_price, 2),
            "peak_date": timestamps[peak_idx],
            "trough_date": timestamps[trough_idx],
        }

    def calculate_drawdown_summary(
        self,
        coin_id: str,
        start_date: str = None
    ) -> Dict:
        """
        Calculate comprehensive drawdown summary for a cryptocurrency.

        Args:
            coin_id: Cryptocurrency identifier
            start_date: Start date in 'YYYY-MM-DD' format (optional)

        Returns:
            Dict with drawdown summary metrics
        """
        history = self.get_price_history(coin_id, start_date)

        if not history:
            return {"error": "No price data found", "coin_id": coin_id}

        prices = [row["price_usd"] for row in history]
        timestamps = [row["time_bucket"] for row in history]
        drawdowns = self.calculate_drawdown_series(prices)

        max_dd = max(drawdowns)
        max_dd_idx = drawdowns.index(max_dd)
        avg_dd = sum(drawdowns) / len(drawdowns) if drawdowns else 0

        # Count days in drawdown
        dd_days = sum(1 for dd in drawdowns if dd > 0)
        total_days = len(drawdowns)
        dd_frequency = (dd_days / total_days * 100) if total_days > 0 else 0

        # Find current status
        current_dd = drawdowns[-1] if drawdowns else 0
        current_price = prices[-1] if prices else 0

        return {
            "coin_id": coin_id,
            "max_drawdown_pct": round(max_dd, 2),
            "avg_drawdown_pct": round(avg_dd, 2),
            "current_drawdown_pct": round(current_dd, 2),
            "max_drawdown_date": timestamps[max_dd_idx].strftime("%Y-%m-%d %H:%M:%S") if max_dd_idx < len(timestamps) else None,
            "current_price": round(current_price, 2),
            "days_in_drawdown": dd_days,
            "total_days": total_days,
            "drawdown_frequency_pct": round(dd_frequency, 2),
            "data_points": len(prices),
            "is_in_drawdown": current_dd > 0,
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
