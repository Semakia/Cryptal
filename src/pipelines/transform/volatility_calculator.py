"""
Volatility Calculator for Crypto Investments
Calculates volatility metrics using pre-aggregated price series data.
Source: crypto_prices_series table (Silver layer)
"""
"""
Volatility Calculator for Crypto Investments
Calculates volatility metrics using pre-aggregated price series data.
Source: crypto_prices_series table (Silver layer)
"""
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor


class VolatilityCalculator:
    """
    Calculates volatility metrics for cryptocurrencies.
    
    Source de données : table crypto_prices_series (Silver layer)
    Cette table contient deja des prix agregees par heure :
    - coin_id : identifiant de la crypto
    - time_bucket : timestamp tronque a l'heure
    - price_usd : prix moyen sur le bucket
    
    Metrics :
    - Period volatility (std dev des returns sur la periode)
    - Annualized volatility
    - Mean, min, max prices
    - Price range
    
    Source de données : table crypto_prices_series (Silver layer)
    Cette table contient deja des prix agregees par heure :
    - coin_id : identifiant de la crypto
    - time_bucket : timestamp tronque a l'heure
    - price_usd : prix moyen sur le bucket
    
    Metrics :
    - Period volatility (std dev des returns sur la periode)
    - Annualized volatility
    - Mean, min, max prices
    - Price range
    """

    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize calculator with database connection.
        
        
        Args:
            db_config: Database configuration dict (SILVER_DB_*)
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
                cursor_factory=RealDictCursor,
            )

    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()

    def calculate_volatility(
        self,
        coin_id: str,
        days: int = 30
    ) -> Optional[Dict]:
        """
        Calculate volatility metrics for a cryptocurrency.

        Utilise directement crypto_prices_series qui contient deja
        les prix agregees par heure. Pas besoin de re-agreger.

        Args:
            coin_id: Cryptocurrency identifier
            days: Number of days to look back (default: 30)
            
        Returns:
            Dictionary with volatility metrics or None
        """
        self.connect()
        cursor = self.conn.cursor()

        # Determiner le facteur d'annualisation selon la granularite
        # crypto_prices_series est agregee par heure -> 8760 periodes/an
        periods_per_year = 365 * 24
        # Determiner le facteur d'annualisation selon la granularite
        # crypto_prices_series est agregee par heure -> 8760 periodes/an
        periods_per_year = 365 * 24

        # La table crypto_prices_series contient deja les prix agregees
        # On calcule directement les returns et leurs statistiques
        query = """
        WITH price_series AS (
            SELECT
                time_bucket,
                price_usd,
                LAG(price_usd) OVER (ORDER BY time_bucket) as prev_price
            FROM crypto_prices_series
            WHERE coin_id = %s
            AND price_usd IS NOT NULL
            AND time_bucket >= NOW() - INTERVAL '1 day' * %s
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
                MIN(price_usd) as min_price,
                MAX(price_usd) as max_price,
                AVG(price_usd) as mean_price
            FROM price_series
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
        # La table crypto_prices_series contient deja les prix agregees
        # On calcule directement les returns et leurs statistiques
        query = """
        WITH price_series AS (
            SELECT
                time_bucket,
                price_usd,
                LAG(price_usd) OVER (ORDER BY time_bucket) as prev_price
            FROM crypto_prices_series
            WHERE coin_id = %s
            AND price_usd IS NOT NULL
            AND time_bucket >= NOW() - INTERVAL '1 day' * %s
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
                MIN(price_usd) as min_price,
                MAX(price_usd) as max_price,
                AVG(price_usd) as mean_price
            FROM price_series
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

        # Annualize volatility
        # Annualize volatility
        annualized_volatility = std_dev_returns * (periods_per_year**0.5)

        # Period volatility (std dev des returns sur la periode)
        # Period volatility (std dev des returns sur la periode)
        period_volatility = std_dev_returns

        # Price range
        # Price range
        price_range = max_price - min_price

        return {
            "coin_id": coin_id,
            "period_days": days,
            "data_points": result["sample_size"],
            "mean_price": mean_price,
            "period_volatility": period_volatility,
            "annualized_volatility": annualized_volatility,
            "period_volatility": period_volatility,
            "annualized_volatility": annualized_volatility,
            "min_price": min_price,
            "max_price": max_price,
            "price_range": price_range,
        }

    def compare_volatility(
        self,
        coin_ids: List[str],
        days: int = 30
    ) -> List[Dict]:
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
        results.sort(key=lambda x: x["annualized_volatility"])
        return results

    def get_risk_adjusted_returns(
        self,
        coin_id: str,
        investment_amount: float,
        days: int = 30
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

        # Get first and last prices from crypto_prices_series
        # Get first and last prices from crypto_prices_series
        cursor.execute(
            """
            SELECT price_usd, time_bucket
            FROM crypto_prices_series
            SELECT price_usd, time_bucket
            FROM crypto_prices_series
            WHERE coin_id = %s
            AND price_usd IS NOT NULL
            AND time_bucket >= NOW() - INTERVAL '1 day' * %s
            ORDER BY time_bucket ASC
            AND price_usd IS NOT NULL
            AND time_bucket >= NOW() - INTERVAL '1 day' * %s
            ORDER BY time_bucket ASC
            LIMIT 1;
            """,
            """,
            (coin_id, days),
        )
        first = cursor.fetchone()

        cursor.execute(
            """
            SELECT price_usd, time_bucket
            FROM crypto_prices_series
            SELECT price_usd, time_bucket
            FROM crypto_prices_series
            WHERE coin_id = %s
            AND price_usd IS NOT NULL
            ORDER BY time_bucket DESC
            AND price_usd IS NOT NULL
            ORDER BY time_bucket DESC
            LIMIT 1;
            """,
            """,
            (coin_id,),
        )
        last = cursor.fetchone()
        cursor.close()

        if not first or not last:
            return vol

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
        """Get list of available cryptocurrencies from crypto_prices_series."""
        """Get list of available cryptocurrencies from crypto_prices_series."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT coin_id
            FROM crypto_prices_series
            FROM crypto_prices_series
            WHERE price_usd IS NOT NULL
            ORDER BY coin_id;
            """
            """
        )
        coins = [row["coin_id"] for row in cursor.fetchall()]
        cursor.close()
        return coins