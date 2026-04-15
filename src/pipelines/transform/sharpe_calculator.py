"""
Sharpe Ratio Calculator for Crypto Investments
Calculates risk-adjusted returns using pre-aggregated price series data.
Source: crypto_prices_series table (Silver layer)
"""
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor


class SharpeCalculator:
    """
    Calculates Sharpe Ratio and risk-adjusted return metrics.
    
    Source de données : table crypto_prices_series (Silver layer)
    Cette table contient deja des prix agregees par heure :
    - coin_id : identifiant de la crypto
    - time_bucket : timestamp tronque a l'heure
    - price_usd : prix moyen sur le bucket
    
    Sharpe Ratio = (Return - Risk-Free Rate) / Volatility
    Higher is better: more return per unit of risk.
    """

    def __init__(self, db_config: Dict[str, str], risk_free_rate: float = 0.05):
        """
        Initialize calculator with database connection.
        
        Args:
            db_config: Database configuration dict (SILVER_DB_*)
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
        
        Utilise crypto_prices_series qui contient deja les prix
        agregees par heure. Pas besoin de re-agreger.
        
        Args:
            coin_id: Cryptocurrency identifier
            days: Analysis period
            
        Returns:
            Return metrics or None
        """
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute(
            """
            WITH period_prices AS (
                SELECT price_usd, time_bucket
                FROM crypto_prices_series
                WHERE coin_id = %s
                AND price_usd IS NOT NULL
                AND time_bucket >= NOW() - INTERVAL '1 day' * %s
                ORDER BY time_bucket ASC
            ),
            first_price AS (
                SELECT price_usd, time_bucket
                FROM period_prices
                LIMIT 1
            ),
            last_price AS (
                SELECT price_usd, time_bucket
                FROM period_prices
                ORDER BY time_bucket DESC
                LIMIT 1
            )
            SELECT
                f.price_usd as first_price,
                f.time_bucket as first_date,
                l.price_usd as last_price,
                l.time_bucket as last_date,
                EXTRACT(EPOCH FROM (l.time_bucket - f.time_bucket)) / 86400 as actual_days,
                (SELECT COUNT(*) FROM period_prices) as data_points
            FROM first_price f, last_price l;
            """,
            (coin_id, days),
        )
        result = cursor.fetchone()
        cursor.close()

        if not result or result["actual_days"] == 0:
            return None

        actual_days = float(result["actual_days"])
        if actual_days < 1:
            return None

        first_price = float(result["first_price"])
        last_price = float(result["last_price"])

        absolute_return = last_price - first_price
        percentage_return = (absolute_return / first_price) * 100
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
            "total_return": percentage_return,
            "annualized_return": annualized_return,
        }

    def calculate_volatility(self, coin_id: str, days: int = 30) -> Optional[float]:
        """
        Calculate annualized volatility (standard deviation) from crypto_prices_series.
        
        La table crypto_prices_series est deja agregee par heure,
        donc on calcule directement les returns sans re-agreger.
        
        Args:
            coin_id: Cryptocurrency identifier
            days: Analysis period
            
        Returns:
            Annualized volatility (%) or None
        """
        self.connect()
        cursor = self.conn.cursor()

        # crypto_prices_series est agregee par heure -> 8760 periodes/an
        periods_per_year = 365 * 24

        query = """
        WITH price_series AS (
            SELECT
                price_usd,
                LAG(price_usd) OVER (ORDER BY time_bucket) as prev_price
            FROM crypto_prices_series
            WHERE coin_id = %s
            AND price_usd IS NOT NULL
            AND time_bucket >= NOW() - INTERVAL '1 day' * %s
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
        rfr = risk_free_rate if risk_free_rate is not None else self.risk_free_rate

        returns = self.calculate_returns(coin_id, days)
        if not returns:
            return {"error": f"No return data available for {coin_id} over {days} days"}

        if returns["period_days"] < 5:
            return {
                "error": f"Insufficient data period for {coin_id}: {returns['period_days']} days (minimum 5 days required)"
            }

        volatility = self.calculate_volatility(coin_id, days)
        if volatility is None or volatility == 0:
            return {
                "error": f"No volatility data available for {coin_id} over {days} days"
            }

        period_risk_free = rfr * (returns["period_days"] / 365)
        excess_return = returns["total_return"] - (period_risk_free * 100)
        period_volatility = volatility / ((365 / returns["period_days"]) ** 0.5)
        sharpe_ratio = excess_return / period_volatility if period_volatility > 0 else 0

        return {
            "coin_id": returns["coin_id"],
            "period_days": returns["period_days"],
            "data_points": returns["data_points"],
            "total_return": returns["total_return"],
            "annualized_return": returns["annualized_return"],
            "annualized_volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "start_price": returns["start_price"],
            "end_price": returns["end_price"],
        }

    def _classify_sharpe(self, sharpe: float) -> str:
        """Classify Sharpe Ratio quality."""
        if sharpe >= 3:
            return "Exceptional"
        elif sharpe >= 2:
            return "Excellent"
        elif sharpe >= 1:
            return "Good"
        elif sharpe >= 0:
            return "Acceptable"
        else:
            return "Poor (Negative)"

    def compare_sharpe_ratios(self, coin_ids: List[str], days: int = 30) -> List[Dict]:
        """Compare Sharpe Ratios across multiple cryptocurrencies."""
        results = []
        for coin_id in coin_ids:
            sharpe = self.calculate_sharpe_ratio(coin_id, days)
            if sharpe:
                results.append(sharpe)
        results.sort(key=lambda x: x["sharpe_ratio"], reverse=True)
        return results

    def find_best_risk_adjusted_investment(
        self, coin_ids: List[str], days: int = 30
    ) -> Optional[Dict]:
        """Find the cryptocurrency with the best risk-adjusted return."""
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
        """Get list of available cryptocurrencies from crypto_prices_series."""
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
