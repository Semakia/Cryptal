"""
Drawdown Calculator for Crypto Investments
Calculates maximum drawdown and recovery metrics.
"""

import os
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

    def calculate_max_drawdown(self, coin_id: str, days: int = 30) -> Optional[Dict]:
        """
        Calculate maximum drawdown for a cryptocurrency.

        Args:
            coin_id: Cryptocurrency identifier
            days: Analysis period

        Returns:
            Drawdown metrics or None
        """
        self.connect()
        cursor = self.conn.cursor()

        # Get price series
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

        prices = cursor.fetchall()
        cursor.close()

        if len(prices) < 2:
            return {"error": f"Insufficient data for {coin_id} over {days} days"}

        # Calculate drawdowns
        max_price_so_far = 0
        max_drawdown = 0
        max_drawdown_info = None
        current_drawdown = 0
        current_peak = None
        recovery_date = None

        peak_timestamp = None
        trough_timestamp = None
        peak_price_value = 0
        trough_price_value = float("inf")

        for record in prices:
            price = float(record["price_usd"])
            timestamp = record["timestamp"]

            # Update running maximum
            if price > max_price_so_far:
                max_price_so_far = price
                current_peak = {"price": price, "timestamp": timestamp}
                # Reset current drawdown when we reach a new peak
                current_drawdown = 0
            else:
                # Calculate drawdown from current peak
                drawdown = ((price - max_price_so_far) / max_price_so_far) * 100
                current_drawdown = drawdown

                # Check if this is the maximum drawdown
                if drawdown < max_drawdown:
                    max_drawdown = drawdown
                    max_drawdown_info = {
                        "peak_price": max_price_so_far,
                        "peak_timestamp": current_peak["timestamp"],
                        "trough_price": price,
                        "trough_timestamp": timestamp,
                        "drawdown_pct": drawdown,
                    }

        # Get current price info
        latest_record = prices[-1]
        latest_price = float(latest_record["price_usd"])
        latest_timestamp = latest_record["timestamp"]

        # Calculate current drawdown from all-time high in this period
        current_drawdown_pct = (
            ((latest_price - max_price_so_far) / max_price_so_far) * 100
            if max_price_so_far > 0
            else 0
        )

        # Check if we've recovered
        has_recovered = latest_price >= max_price_so_far * 0.99  # Within 1% of peak

        # Calculate recovery time if applicable
        recovery_time_days = None
        if max_drawdown_info and has_recovered:
            recovery_time = latest_timestamp - max_drawdown_info["trough_timestamp"]
            recovery_time_days = recovery_time.total_seconds() / 86400

        # Calculate underwater percentage
        underwater_result = self.calculate_underwater_periods(coin_id, days)
        underwater_pct = (
            underwater_result["underwater_pct"] if underwater_result else 0.0
        )

        # Extract peak and trough info
        peak_price = (
            max_drawdown_info["peak_price"] if max_drawdown_info else max_price_so_far
        )
        trough_price = (
            max_drawdown_info["trough_price"] if max_drawdown_info else latest_price
        )
        peak_date = max_drawdown_info["peak_timestamp"] if max_drawdown_info else None
        trough_date = (
            max_drawdown_info["trough_timestamp"] if max_drawdown_info else None
        )

        # Calculate max drawdown value in absolute terms
        max_drawdown_value = peak_price - trough_price if max_drawdown_info else 0.0

        # Calculate drawdown periods for chart
        drawdown_periods = self._calculate_drawdown_periods_from_prices(prices)

        return {
            "coin_id": coin_id,
            "period_days": days,
            "data_points": len(prices),
            "max_drawdown_pct": max_drawdown,
            "max_drawdown_value": max_drawdown_value,
            "current_drawdown_pct": current_drawdown_pct,
            "underwater_pct": underwater_pct,
            "peak_price": peak_price,
            "trough_price": trough_price,
            "current_price": latest_price,
            "peak_date": peak_date,
            "trough_date": trough_date,
            "drawdown_periods": drawdown_periods,
        }

    def _calculate_drawdown_periods_from_prices(self, prices: List[Dict]) -> List[Dict]:
        """
        Calculate drawdown periods from price data for charting.

        Args:
            prices: List of price records with timestamp and price_usd

        Returns:
            List of drawdown period dicts with start, drawdown values
        """
        if len(prices) < 2:
            return []

        drawdown_periods = []
        max_price_so_far = 0

        for record in prices:
            price = float(record["price_usd"])
            timestamp = record["timestamp"]

            # Update running maximum
            if price > max_price_so_far:
                max_price_so_far = price

            # Calculate drawdown from peak
            if max_price_so_far > 0:
                drawdown = (price - max_price_so_far) / max_price_so_far
            else:
                drawdown = 0

            drawdown_periods.append(
                {"start": timestamp.isoformat(), "drawdown": drawdown}
            )

        return drawdown_periods

    def _classify_drawdown_risk(self, drawdown_pct: float) -> str:
        """
        Classify drawdown risk level.

        Args:
            drawdown_pct: Maximum drawdown percentage (negative)

        Returns:
            Risk classification
        """
        abs_dd = abs(drawdown_pct)

        if abs_dd < 5:
            return "🟢 Very Low Risk (< 5% drop)"
        elif abs_dd < 10:
            return "🟡 Low Risk (5-10% drop)"
        elif abs_dd < 20:
            return "🟠 Moderate Risk (10-20% drop)"
        elif abs_dd < 30:
            return "🔴 High Risk (20-30% drop)"
        else:
            return "⚫ Extreme Risk (> 30% drop)"

    def compare_drawdowns(self, coin_ids: List[str], days: int = 30) -> List[Dict]:
        """
        Compare maximum drawdowns across multiple cryptocurrencies.

        Args:
            coin_ids: List of cryptocurrency identifiers
            days: Analysis period

        Returns:
            List of drawdown metrics, sorted by risk (best to worst)
        """
        results = []

        for coin_id in coin_ids:
            dd = self.calculate_max_drawdown(coin_id, days)
            if dd and "error" not in dd:
                results.append(dd)

        # Sort by max drawdown (least negative = least risky)
        results.sort(key=lambda x: x["max_drawdown_pct"], reverse=True)

        return results

    def calculate_underwater_periods(self, coin_id: str, days: int = 30) -> Dict:
        """
        Calculate how long the crypto has been "underwater" (below previous high).

        Args:
            coin_id: Cryptocurrency identifier
            days: Analysis period

        Returns:
            Underwater period statistics
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute(
            """
            WITH price_series AS (
                SELECT
                    timestamp,
                    price_usd,
                    MAX(price_usd) OVER (
                        ORDER BY timestamp
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ) as running_max
                FROM crypto_prices
                WHERE coin_id = %s
                  AND price_usd IS NOT NULL
                  AND timestamp >= NOW() - INTERVAL '1 day' * %s
            ),
            underwater_status AS (
                SELECT
                    timestamp,
                    price_usd,
                    running_max,
                    CASE
                        WHEN price_usd < running_max * 0.99 THEN 1
                        ELSE 0
                    END as is_underwater
                FROM price_series
            )
            SELECT
                COUNT(*) as total_periods,
                SUM(is_underwater) as underwater_periods,
                (SUM(is_underwater)::FLOAT / COUNT(*)::FLOAT * 100) as underwater_pct
            FROM underwater_status;
        """,
            (coin_id, days),
        )

        result = cursor.fetchone()
        cursor.close()

        if not result:
            return None

        return {
            "coin_id": coin_id,
            "total_periods": result["total_periods"],
            "underwater_periods": result["underwater_periods"],
            "underwater_pct": float(result["underwater_pct"])
            if result["underwater_pct"]
            else 0,
            "above_water_pct": 100
            - (float(result["underwater_pct"]) if result["underwater_pct"] else 0),
        }

    def calculate_drawdown_duration(
        self, coin_id: str, days: int = 30
    ) -> Optional[Dict]:
        """
        Calculate the duration of the maximum drawdown event.

        Args:
            coin_id: Cryptocurrency identifier
            days: Analysis period

        Returns:
            Drawdown duration metrics
        """
        dd = self.calculate_max_drawdown(coin_id, days)
        if not dd or "error" in dd:
            return None

        # Reconstruct max_drawdown_info from dd fields
        dd_info = {
            "peak_price": dd["peak_price"],
            "peak_timestamp": dd["peak_date"],
            "trough_price": dd["trough_price"],
            "trough_timestamp": dd["trough_date"],
            "drawdown_pct": dd["max_drawdown_pct"],
        }

        # Duration from peak to trough
        decline_duration = dd_info["trough_timestamp"] - dd_info["peak_timestamp"]
        decline_days = decline_duration.total_seconds() / 86400

        result = {
            **dd,
            "decline_duration_days": decline_days,
            "decline_duration_hours": decline_duration.total_seconds() / 3600,
        }

        # Add recovery info if available
        if dd["recovery_time_days"]:
            result["total_drawdown_duration_days"] = (
                decline_days + dd["recovery_time_days"]
            )

        return result

    def get_worst_investment_timing(
        self, coin_id: str, days: int = 30
    ) -> Optional[Dict]:
        """
        Find the worst possible time to have bought (at the peak before max drawdown).

        Args:
            coin_id: Cryptocurrency identifier
            days: Analysis period

        Returns:
            Worst timing analysis
        """
        dd = self.calculate_max_drawdown(coin_id, days)
        if not dd or "error" in dd:
            return None

        # Reconstruct max_drawdown_info from dd fields
        dd_info = {
            "peak_price": dd["peak_price"],
            "peak_timestamp": dd["peak_date"],
            "trough_price": dd["trough_price"],
            "trough_timestamp": dd["trough_date"],
            "drawdown_pct": dd["max_drawdown_pct"],
        }

        # Simulate investment at the worst time
        investment_amount = 1000  # $1000 example
        bought_at = dd_info["peak_price"]
        quantity = investment_amount / bought_at

        # Value at trough (worst point)
        value_at_trough = quantity * dd_info["trough_price"]
        loss_at_trough = value_at_trough - investment_amount

        # Current value
        current_value = quantity * dd["current_price"]
        current_pnl = current_value - investment_amount

        return {
            "coin_id": coin_id,
            "worst_buy_date": dd_info["peak_timestamp"],
            "worst_buy_price": dd_info["peak_price"],
            "investment_amount": investment_amount,
            "quantity": quantity,
            "trough_date": dd_info["trough_timestamp"],
            "trough_price": dd_info["trough_price"],
            "value_at_trough": value_at_trough,
            "loss_at_trough": loss_at_trough,
            "loss_pct_at_trough": dd_info["drawdown_pct"],
            "current_price": dd["current_price"],
            "current_value": current_value,
            "current_pnl": current_pnl,
            "current_pnl_pct": ((current_value - investment_amount) / investment_amount)
            * 100,
            "has_recovered": current_value >= investment_amount * 0.99,
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
