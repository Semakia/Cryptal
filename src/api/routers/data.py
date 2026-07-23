"""
Data router for basic cryptocurrency data endpoints.
Provides access to raw price data and cryptocurrency information.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from database import DatabaseConnection, get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models import CryptoInfo, LatestPrices, PriceData

router = APIRouter(prefix="/data", tags=["Data"])

# Cryptocurrencies to exclude from all endpoints
EXCLUDED_CRYPTOS = ["ripple", "tether"]


@router.get("/cryptos", response_model=List[CryptoInfo])
async def get_cryptocurrencies(db: DatabaseConnection = Depends(get_db)):
    """
    Get list of all tracked cryptocurrencies with their data ranges.

    Returns
    -------
    List[CryptoInfo]
        List of cryptocurrencies with metadata.
    """
    cursor = db.get_cursor()
    try:
        cursor.execute(
            """
            SELECT
                coin_id,
                COUNT(*) as data_points,
                MIN(timestamp) as earliest_date,
                MAX(timestamp) as latest_date
            FROM crypto_prices
            WHERE coin_id NOT IN %s
            GROUP BY coin_id
            ORDER BY coin_id
            """,
            (tuple(EXCLUDED_CRYPTOS),),
        )
        results = cursor.fetchall()
        return [
            CryptoInfo(
                coin_id=row["coin_id"],
                data_points=row["data_points"],
                earliest_date=row["earliest_date"],
                latest_date=row["latest_date"],
            )
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()


@router.get("/prices", response_model=List[PriceData])
async def get_prices(
    crypto: Optional[str] = Query(None, description="Filter by cryptocurrency ID"),
    days: int = Query(7, ge=1, le=365, description="Number of days to retrieve"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of records"),
    db: DatabaseConnection = Depends(get_db),
):
    """
    Get historical price data with optional filters.

    Parameters
    ----------
    crypto : str, optional
        Cryptocurrency ID to filter by (e.g., 'bitcoin').
    days : int, default=7
        Number of days of historical data to retrieve.
    limit : int, default=1000
        Maximum number of records to return.

    Returns
    -------
    List[PriceData]
        List of price data points.
    """
    cursor = db.get_cursor()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        if crypto:
            query = """
                SELECT id, coin_id, price_usd, price_eur, price_gbp,
                       change_24h, market_cap, timestamp
                FROM crypto_prices
                WHERE coin_id = %s AND timestamp >= %s AND coin_id NOT IN %s
                ORDER BY timestamp DESC
                LIMIT %s
            """
            cursor.execute(query, (crypto, cutoff_date, tuple(EXCLUDED_CRYPTOS), limit))
        else:
            query = """
                SELECT id, coin_id, price_usd, price_eur, price_gbp,
                       change_24h, market_cap, timestamp
                FROM crypto_prices
                WHERE timestamp >= %s AND coin_id NOT IN %s
                ORDER BY timestamp DESC
                LIMIT %s
            """
            cursor.execute(query, (cutoff_date, tuple(EXCLUDED_CRYPTOS), limit))

        results = cursor.fetchall()
        return [PriceData(**row) for row in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()


@router.get("/prices/latest", response_model=LatestPrices)
async def get_latest_prices(db: DatabaseConnection = Depends(get_db)):
    """
    Get the most recent price for each cryptocurrency.

    Returns
    -------
    LatestPrices
        Latest prices for all tracked cryptocurrencies.
    """
    cursor = db.get_cursor()
    try:
        # Get latest price for each crypto using DISTINCT ON
        query = """
            SELECT DISTINCT ON (coin_id)
                id, coin_id, price_usd, price_eur, price_gbp,
                change_24h, market_cap, timestamp
            FROM crypto_prices
            WHERE coin_id NOT IN %s
            ORDER BY coin_id, timestamp DESC
        """
        cursor.execute(query, (tuple(EXCLUDED_CRYPTOS),))
        results = cursor.fetchall()

        if not results:
            return LatestPrices(data=[], count=0, last_update=None)

        prices = [PriceData(**row) for row in results]
        last_update = max(p.timestamp for p in prices) if prices else None

        return LatestPrices(data=prices, count=len(prices), last_update=last_update)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()


@router.get("/prices/{crypto_id}", response_model=List[PriceData])
async def get_crypto_prices(
    crypto_id: str,
    days: int = Query(7, ge=1, le=365, description="Number of days to retrieve"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum number of records"),
    db: DatabaseConnection = Depends(get_db),
):
    """
    Get historical price data for a specific cryptocurrency.
    Data is aggregated based on the period:
    - 1 day: hourly intervals (24 points)
    - 7 days: every 6 hours (28 points)
    - 30 days: daily intervals (30 points)
    - 90+ days: every 3 days

    Parameters
    ----------
    crypto_id : str
        Cryptocurrency ID (e.g., 'bitcoin', 'ethereum').
    days : int, default=7
        Number of days of historical data to retrieve.
    limit : int, default=1000
        Maximum number of records to return.

    Returns
    -------
    List[PriceData]
        List of aggregated price data points for the specified cryptocurrency.
    """
    cursor = db.get_cursor()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Determine aggregation interval based on period
        if days <= 1:
            # 24h: aggregate by hour (24 points)
            interval = "1 hour"
            trunc_format = "hour"
        elif days <= 7:
            # 7 days: aggregate every 6 hours (~28 points)
            interval = "6 hours"
            trunc_format = "hour"
        elif days <= 30:
            # 30 days: aggregate daily (30 points)
            interval = "1 day"
            trunc_format = "day"
        else:
            # 90+ days: aggregate every 3 days
            interval = "3 days"
            trunc_format = "day"

        # Use date_trunc for aggregation to get evenly distributed points
        query = """
            WITH aggregated AS (
                SELECT
                    MAX(id) as id,
                    coin_id,
                    AVG(price_usd) as price_usd,
                    AVG(price_eur) as price_eur,
                    AVG(price_gbp) as price_gbp,
                    AVG(change_24h) as change_24h,
                    AVG(market_cap) as market_cap,
                    date_trunc(%s, timestamp) as timestamp
                FROM crypto_prices
                WHERE coin_id = %s AND timestamp >= %s
                GROUP BY coin_id, date_trunc(%s, timestamp)
                ORDER BY timestamp ASC
            )
            SELECT * FROM aggregated
            LIMIT %s
        """
        cursor.execute(
            query, (trunc_format, crypto_id, cutoff_date, trunc_format, limit)
        )
        results = cursor.fetchall()

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for cryptocurrency '{crypto_id}'",
            )

        return [PriceData(**row) for row in results]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
