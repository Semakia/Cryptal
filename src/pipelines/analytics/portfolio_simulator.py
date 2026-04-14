"""
PnL Portfolio Simulator for Crypto Investments
Allows backtesting investment strategies on historical data.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor


def to_naive_utc(dt: datetime) -> datetime:
    """
    Ensure datetime is naive UTC (no tzinfo).
    """
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt
class PortfolioSimulator:
    """
    Simulates cryptocurrency investment portfolios and calculates P&L.
    
    Features:
    - Single crypto investment simulation
    - Multiple crypto comparison
    - Historical performance analysis
    """

    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize the simulator with database connection.
        
        Args:
            db_config: Database configuration dict with keys:
                      host, dbname, user, password, port
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

    def get_price_at_date(
        self, coin_id: str, target_date: datetime
    ) -> Optional[float]:
        """
        Get the price of a crypto at a specific date.
        
        Args:
            coin_id: Cryptocurrency identifier (e.g., 'bitcoin')
            target_date: Target date for price lookup
            
        Returns:
            Price in USD or None if not found
        """
        self.connect()
        cursor = self.conn.cursor()

        # Find closest price to target date
        cursor.execute(
            """
            SELECT price_usd, timestamp,
                   ABS(EXTRACT(EPOCH FROM (timestamp - %s))) as time_diff
            FROM crypto_prices
            WHERE coin_id = %s
              AND price_usd IS NOT NULL
            ORDER BY time_diff ASC
            LIMIT 1;
        """,
            (target_date, coin_id),
        )

        result = cursor.fetchone()
        cursor.close()

        if result:
            return float(result["price_usd"])
        return None

    def get_latest_price(self, coin_id: str) -> Optional[float]:
        """
        Get the latest available price for a crypto.
        
        Args:
            coin_id: Cryptocurrency identifier
            
        Returns:
            Latest price in USD or None
        """
        self.connect()
        cursor = self.conn.cursor()

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

        result = cursor.fetchone()
        cursor.close()

        if result:
            return float(result["price_usd"])
        return None

    def simulate_investment(
        self,
        coin_id: str,
        investment_amount: float,
        purchase_date: datetime,
        sell_date: Optional[datetime] = None,
    ) -> Dict:
        """
        Simulate a single crypto investment.
        
        Args:
            coin_id: Cryptocurrency to invest in
            investment_amount: Amount in USD to invest
            purchase_date: Date of purchase
            sell_date: Date of sale (None = latest available)
            
        Returns:
            Dictionary with investment details and P&L
        """
        # Get purchase price
        purchase_price = self.get_price_at_date(coin_id, purchase_date)
        if not purchase_price:
            return {
                "error": f"No price data available for {coin_id} at {purchase_date}",
                "coin_id": coin_id,
            }

        # Get sell price
        if sell_date:
            sell_price = self.get_price_at_date(coin_id, sell_date)
        else:
            sell_price = self.get_latest_price(coin_id)

        if not sell_price:
            return {
                "error": f"No sell price available for {coin_id}",
                "coin_id": coin_id,
            }

        # Calculate investment metrics
        quantity = investment_amount / purchase_price
        current_value = quantity * sell_price
        pnl = current_value - investment_amount
        pnl_percentage = (pnl / investment_amount) * 100

        return {
            "coin_id": coin_id,
            "investment_amount": investment_amount,
            "purchase_date": purchase_date,
            "purchase_price": purchase_price,
            "sell_date": sell_date or "latest",
            "sell_price": sell_price,
            "quantity": quantity,
            "current_value": current_value,
            "pnl": pnl,
            "pnl_percentage": pnl_percentage,
            "roi": pnl_percentage,
        }

    def compare_investments(
        self,
        coin_ids: List[str],
        investment_amount: float,
        purchase_date: datetime,
        sell_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Compare investment performance across multiple cryptos.
        
        Args:
            coin_ids: List of cryptocurrencies to compare
            investment_amount: Amount in USD to invest in each
            purchase_date: Date of purchase
            sell_date: Date of sale (None = latest)
            
        Returns:
            List of investment results, sorted by P&L
        """
        results = []

        for coin_id in coin_ids:
            result = self.simulate_investment(
                coin_id, investment_amount, purchase_date, sell_date
            )
            if "error" not in result:
                results.append(result)

        # Sort by P&L (best to worst)
        results.sort(key=lambda x: x["pnl"], reverse=True)

        return results

    def get_best_entry_point(
        self, coin_id: str, investment_amount: float, lookback_days: int = 30
    ) -> Dict:
        """
        Find the best historical entry point for an investment over a lookback period.
        """

        self.connect()
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT timestamp, price_usd
            FROM crypto_prices
            WHERE coin_id = %s
                AND price_usd IS NOT NULL
                AND timestamp <= (NOW() AT TIME ZONE 'UTC')
                AND timestamp >= (NOW() AT TIME ZONE 'UTC') - INTERVAL '1 day' * %s
            ORDER BY timestamp ASC;
            """,
            (coin_id, lookback_days),
        )

        historical_prices = cursor.fetchall()
        cursor.close()

        if not historical_prices:
            return {"error": "No valid historical data in time range"}

        latest_price = self.get_latest_price(coin_id)
        if not latest_price:
            return {"error": f"No latest price for {coin_id}"}

        best_result = None
        best_pnl = float("-inf")

        for record in historical_prices:
            purchase_price = float(record["price_usd"])
            quantity = investment_amount / purchase_price
            current_value = quantity * latest_price
            pnl = current_value - investment_amount

            if pnl > best_pnl:
                best_pnl = pnl
                best_result = {
                    "coin_id": coin_id,
                    "best_entry_date": to_naive_utc(record["timestamp"]),  
                    "best_entry_price": purchase_price,
                    "investment_amount": investment_amount,
                    "quantity": quantity,
                    "current_price": latest_price,
                    "current_value": current_value,
                    "pnl": pnl,
                    "pnl_percentage": (pnl / investment_amount) * 100,
                }

        return best_result

    def get_available_coins(self) -> List[str]:
        """
        Get list of available cryptocurrencies in the database.
        
        Returns:
            List of coin IDs
        """
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

    def get_date_range(self, coin_id: str) -> Tuple[datetime, datetime]:
        """
        Get the available date range for a cryptocurrency.
        
        Args:
            coin_id: Cryptocurrency identifier
            
        Returns:
            Tuple of (earliest_date, latest_date)
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT
                MIN(timestamp) as earliest,
                MAX(timestamp) as latest
            FROM crypto_prices
            WHERE coin_id = %s
              AND price_usd IS NOT NULL;
        """,
            (coin_id,),
        )

        result = cursor.fetchone()
        cursor.close()

        if result:
            return (result["earliest"], result["latest"])
        return (None, None)
