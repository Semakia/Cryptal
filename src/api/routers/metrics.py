"""
Metrics router for cryptocurrency analytics endpoints.
Provides volatility, Sharpe ratio, drawdown, and correlation metrics.
"""

<<<<<<< HEAD
=======
import logging
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

<<<<<<< HEAD
=======
logger = logging.getLogger(__name__)

>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from database import DatabaseConnection, get_db, get_db_config
from models import (
    CorrelationMatrix,
    CorrelationPair,
    DrawdownMetrics,
    ErrorResponse,
    SharpeMetrics,
    VolatilityMetrics,
)
from pipelines.transform.correlation_calculator import CorrelationCalculator
from pipelines.transform.drawdown_calculator import DrawdownCalculator
from pipelines.transform.sharpe_calculator import SharpeCalculator
from pipelines.transform.volatility_calculator import VolatilityCalculator

router = APIRouter(prefix="/metrics", tags=["Metrics"])

<<<<<<< HEAD
=======
# Cryptocurrencies to exclude from all endpoints
EXCLUDED_CRYPTOS = ["ripple", "tether"]

>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1

@router.get("/volatility", response_model=List[VolatilityMetrics])
async def get_volatility_all(
    period: int = Query(7, ge=1, le=365, description="Period in days"),
    db: DatabaseConnection = Depends(get_db),
):
    """
    Get volatility metrics for all cryptocurrencies.

    Parameters
    ----------
    period : int, default=7
        Period in days to calculate volatility over.

    Returns
    -------
    List[VolatilityMetrics]
        Volatility metrics for all tracked cryptocurrencies.
    """
    try:
        calculator = VolatilityCalculator(get_db_config())

<<<<<<< HEAD
        # Get all available coins
        cursor = db.get_cursor()
        cursor.execute("SELECT DISTINCT coin_id FROM crypto_prices ORDER BY coin_id")
=======
        # Get all available coins (excluding unwanted ones)
        cursor = db.get_cursor()
        cursor.execute(
            "SELECT DISTINCT coin_id FROM crypto_prices WHERE coin_id NOT IN %s ORDER BY coin_id",
            (tuple(EXCLUDED_CRYPTOS),),
        )
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        coins = [row["coin_id"] for row in cursor.fetchall()]
        cursor.close()

        results = []
        for coin in coins:
            try:
                metrics = calculator.calculate_volatility(coin, period)
                if "error" not in metrics:
                    results.append(
                        VolatilityMetrics(
                            coin_id=metrics["coin_id"],
                            period_days=metrics["period_days"],
                            data_points=metrics["data_points"],
                            mean_price=metrics["mean_price"],
<<<<<<< HEAD
                            std_dev=metrics["std_dev"],
                            annualized_volatility=metrics["annualized_volatility"],
                            variance=metrics["variance"],
                            coefficient_of_variation=metrics[
                                "coefficient_of_variation"
                            ],
                            var_95=metrics["var_95"],
                            min_price=metrics["min_price"],
                            max_price=metrics["max_price"],
                            price_range=metrics["price_range"],
=======
                            period_volatility=metrics["period_volatility"],
                            annualized_volatility=metrics["annualized_volatility"],
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
                        )
                    )
            except Exception:
                # Skip coins with insufficient data
                continue

        calculator.close()

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No volatility data available for period of {period} days",
            )

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.get("/volatility/{crypto_id}", response_model=VolatilityMetrics)
async def get_volatility(
    crypto_id: str,
    period: int = Query(7, ge=1, le=365, description="Period in days"),
):
    """
    Get volatility metrics for a specific cryptocurrency.

    Parameters
    ----------
    crypto_id : str
        Cryptocurrency ID (e.g., 'bitcoin', 'ethereum').
    period : int, default=7
        Period in days to calculate volatility over.

    Returns
    -------
    VolatilityMetrics
        Volatility metrics for the specified cryptocurrency.
    """
    try:
        calculator = VolatilityCalculator(get_db_config())
        metrics = calculator.calculate_volatility(crypto_id, period)
        calculator.close()

        if "error" in metrics:
            raise HTTPException(status_code=404, detail=metrics["error"])

        return VolatilityMetrics(
            coin_id=metrics["coin_id"],
            period_days=metrics["period_days"],
            data_points=metrics["data_points"],
            mean_price=metrics["mean_price"],
<<<<<<< HEAD
            std_dev=metrics["std_dev"],
            annualized_volatility=metrics["annualized_volatility"],
            variance=metrics["variance"],
            coefficient_of_variation=metrics["coefficient_of_variation"],
            var_95=metrics["var_95"],
            min_price=metrics["min_price"],
            max_price=metrics["max_price"],
            price_range=metrics["price_range"],
=======
            period_volatility=metrics["period_volatility"],
            annualized_volatility=metrics["annualized_volatility"],
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.get("/sharpe", response_model=List[SharpeMetrics])
async def get_sharpe_all(
    period: int = Query(30, ge=1, le=365, description="Period in days"),
    risk_free_rate: float = Query(0.02, ge=0, le=0.2, description="Risk-free rate"),
    db: DatabaseConnection = Depends(get_db),
):
    """
<<<<<<< HEAD
    Get Sharpe and Sortino ratios for all cryptocurrencies.
=======
    Get Sharpe ratios for all cryptocurrencies.
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1

    Parameters
    ----------
    period : int, default=30
        Period in days to calculate ratios over.
    risk_free_rate : float, default=0.02
        Annual risk-free rate (default 2%).

    Returns
    -------
    List[SharpeMetrics]
        Sharpe metrics for all tracked cryptocurrencies.
    """
    try:
        calculator = SharpeCalculator(get_db_config())

<<<<<<< HEAD
        # Get all available coins
        cursor = db.get_cursor()
        cursor.execute("SELECT DISTINCT coin_id FROM crypto_prices ORDER BY coin_id")
=======
        # Get all available coins (excluding unwanted ones)
        cursor = db.get_cursor()
        cursor.execute(
            "SELECT DISTINCT coin_id FROM crypto_prices WHERE coin_id NOT IN %s ORDER BY coin_id",
            (tuple(EXCLUDED_CRYPTOS),),
        )
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        coins = [row["coin_id"] for row in cursor.fetchall()]
        cursor.close()

        results = []
        for coin in coins:
            try:
                metrics = calculator.calculate_sharpe_ratio(
                    coin, period, risk_free_rate
                )
<<<<<<< HEAD
                if "error" not in metrics and metrics["period_days"] >= 5:
                    results.append(
                        SharpeMetrics(
                            coin_id=metrics["coin_id"],
                            period_days=metrics["period_days"],
                            data_points=metrics["data_points"],
                            total_return=metrics["total_return"],
                            annualized_return=metrics["annualized_return"],
                            annualized_volatility=metrics["annualized_volatility"],
                            sharpe_ratio=metrics["sharpe_ratio"],
                            sortino_ratio=metrics["sortino_ratio"],
                            start_price=metrics["start_price"],
                            end_price=metrics["end_price"],
                        )
                    )
            except Exception:
                # Skip coins with insufficient data
=======
                if "error" in metrics:
                    logger.warning(
                        f"Sharpe calculation error for {coin}: {metrics.get('error')}"
                    )
                    continue
                # Allow 1+ day calculations (previously required 5+ days)
                if metrics["period_days"] < 1:
                    logger.warning(
                        f"Sharpe: {coin} has only {metrics['period_days']} days (minimum 1 required)"
                    )
                    continue

                logger.info(
                    f"Sharpe: {coin} - period_days={metrics['period_days']}, sharpe={metrics['sharpe_ratio']:.2f}"
                )
                results.append(
                    SharpeMetrics(
                        coin_id=metrics["coin_id"],
                        period_days=metrics["period_days"],
                        data_points=metrics["data_points"],
                        total_return=metrics["total_return"],
                        annualized_return=metrics["annualized_return"],
                        annualized_volatility=metrics["annualized_volatility"],
                        sharpe_ratio=metrics["sharpe_ratio"],
                        start_price=metrics["start_price"],
                        end_price=metrics["end_price"],
                    )
                )
            except Exception as e:
                # Skip coins with insufficient data
                logger.error(f"Sharpe calculation exception for {coin}: {str(e)}")
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
                continue

        calculator.close()

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No Sharpe ratio data available for period of {period} days",
            )

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.get("/sharpe/{crypto_id}", response_model=SharpeMetrics)
async def get_sharpe(
    crypto_id: str,
    period: int = Query(30, ge=1, le=365, description="Period in days"),
    risk_free_rate: float = Query(0.02, ge=0, le=0.2, description="Risk-free rate"),
):
    """
<<<<<<< HEAD
    Get Sharpe and Sortino ratios for a specific cryptocurrency.
=======
    Get Sharpe ratio for a specific cryptocurrency.
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1

    Parameters
    ----------
    crypto_id : str
        Cryptocurrency ID (e.g., 'bitcoin', 'ethereum').
    period : int, default=30
        Period in days to calculate ratios over.
    risk_free_rate : float, default=0.02
        Annual risk-free rate (default 2%).

    Returns
    -------
    SharpeMetrics
        Sharpe metrics for the specified cryptocurrency.
    """
    try:
        calculator = SharpeCalculator(get_db_config())
        metrics = calculator.calculate_sharpe_ratio(crypto_id, period, risk_free_rate)
        calculator.close()

        if "error" in metrics:
            raise HTTPException(status_code=404, detail=metrics["error"])

        if metrics["period_days"] < 5:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient data period: {metrics['period_days']} days (minimum 5 days required for reliable Sharpe calculation)",
            )

        return SharpeMetrics(
            coin_id=metrics["coin_id"],
            period_days=metrics["period_days"],
            data_points=metrics["data_points"],
            total_return=metrics["total_return"],
            annualized_return=metrics["annualized_return"],
            annualized_volatility=metrics["annualized_volatility"],
            sharpe_ratio=metrics["sharpe_ratio"],
<<<<<<< HEAD
            sortino_ratio=metrics["sortino_ratio"],
=======
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
            start_price=metrics["start_price"],
            end_price=metrics["end_price"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.get("/drawdown", response_model=List[DrawdownMetrics])
async def get_drawdown_all(
    period: int = Query(30, ge=1, le=365, description="Period in days"),
    db: DatabaseConnection = Depends(get_db),
):
    """
    Get maximum drawdown metrics for all cryptocurrencies.

    Parameters
    ----------
    period : int, default=30
        Period in days to calculate drawdown over.

    Returns
    -------
    List[DrawdownMetrics]
        Drawdown metrics for all tracked cryptocurrencies.
    """
    try:
        calculator = DrawdownCalculator(get_db_config())

<<<<<<< HEAD
        # Get all available coins
        cursor = db.get_cursor()
        cursor.execute("SELECT DISTINCT coin_id FROM crypto_prices ORDER BY coin_id")
=======
        # Get all available coins (excluding unwanted ones)
        cursor = db.get_cursor()
        cursor.execute(
            "SELECT DISTINCT coin_id FROM crypto_prices WHERE coin_id NOT IN %s ORDER BY coin_id",
            (tuple(EXCLUDED_CRYPTOS),),
        )
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        coins = [row["coin_id"] for row in cursor.fetchall()]
        cursor.close()

        results = []
        for coin in coins:
            try:
                metrics = calculator.calculate_max_drawdown(coin, period)
                if "error" not in metrics:
                    results.append(
                        DrawdownMetrics(
                            coin_id=metrics["coin_id"],
                            period_days=metrics["period_days"],
                            data_points=metrics["data_points"],
                            max_drawdown_pct=metrics["max_drawdown_pct"],
                            max_drawdown_value=metrics["max_drawdown_value"],
<<<<<<< HEAD
                            current_drawdown_pct=metrics["current_drawdown_pct"],
                            underwater_pct=metrics["underwater_pct"],
                            peak_price=metrics["peak_price"],
                            trough_price=metrics["trough_price"],
                            current_price=metrics["current_price"],
                            peak_date=metrics["peak_date"],
                            trough_date=metrics["trough_date"],
                            drawdown_periods=metrics.get("drawdown_periods", []),
=======
                            peak_price=metrics["peak_price"],
                            trough_price=metrics["trough_price"],
                            peak_date=metrics["peak_date"],
                            trough_date=metrics["trough_date"],
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
                        )
                    )
            except Exception:
                # Skip coins with insufficient data
                continue

        calculator.close()

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No drawdown data available for period of {period} days",
            )

        return results

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.get("/drawdown/{crypto_id}", response_model=DrawdownMetrics)
async def get_drawdown(
    crypto_id: str,
    period: int = Query(30, ge=1, le=365, description="Period in days"),
):
    """
    Get maximum drawdown metrics for a specific cryptocurrency.

    Parameters
    ----------
    crypto_id : str
        Cryptocurrency ID (e.g., 'bitcoin', 'ethereum').
    period : int, default=30
        Period in days to calculate drawdown over.

    Returns
    -------
    DrawdownMetrics
        Drawdown metrics for the specified cryptocurrency.
    """
    try:
        calculator = DrawdownCalculator(get_db_config())
        metrics = calculator.calculate_max_drawdown(crypto_id, period)
        calculator.close()

        if "error" in metrics:
            raise HTTPException(status_code=404, detail=metrics["error"])

        return DrawdownMetrics(
            coin_id=metrics["coin_id"],
            period_days=metrics["period_days"],
            data_points=metrics["data_points"],
            max_drawdown_pct=metrics["max_drawdown_pct"],
            max_drawdown_value=metrics["max_drawdown_value"],
<<<<<<< HEAD
            current_drawdown_pct=metrics["current_drawdown_pct"],
            underwater_pct=metrics["underwater_pct"],
            peak_price=metrics["peak_price"],
            trough_price=metrics["trough_price"],
            current_price=metrics["current_price"],
            peak_date=metrics["peak_date"],
            trough_date=metrics["trough_date"],
            drawdown_periods=metrics.get("drawdown_periods", []),
=======
            peak_price=metrics["peak_price"],
            trough_price=metrics["trough_price"],
            peak_date=metrics["peak_date"],
            trough_date=metrics["trough_date"],
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.get("/correlation", response_model=CorrelationMatrix)
async def get_correlation_matrix(
    period: int = Query(30, ge=1, le=365, description="Period in days"),
):
    """
    Get correlation matrix for all cryptocurrency pairs.

    Parameters
    ----------
    period : int, default=30
        Period in days to calculate correlation over.

    Returns
    -------
    CorrelationMatrix
        Correlation matrix with diversification metrics.
    """
    try:
        calculator = CorrelationCalculator(get_db_config())

<<<<<<< HEAD
        # Get all available coins
=======
        # Get all available coins (excluding unwanted ones)
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        db_config = get_db_config()
        import psycopg2

        conn = psycopg2.connect(
            host=db_config["host"],
            dbname=db_config["dbname"],
            user=db_config["user"],
            password=db_config["password"],
            port=db_config["port"],
            sslmode="require",
        )
        cursor = conn.cursor()
<<<<<<< HEAD
        cursor.execute("SELECT DISTINCT coin_id FROM crypto_prices ORDER BY coin_id")
=======
        cursor.execute(
            "SELECT DISTINCT coin_id FROM crypto_prices WHERE coin_id NOT IN %s ORDER BY coin_id",
            (tuple(EXCLUDED_CRYPTOS),),
        )
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        coins = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        if len(coins) < 2:
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 cryptocurrencies to calculate correlation",
            )

        result = calculator.calculate_correlation_matrix(coins, period)
        calculator.close()

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        # Convert matrix to list of pairs
        correlations = []
        for (crypto_1, crypto_2), corr_value in result["correlation_matrix"].items():
            correlations.append(
                CorrelationPair(
                    crypto_1=crypto_1, crypto_2=crypto_2, correlation=corr_value
                )
            )

<<<<<<< HEAD
        # Find highest and lowest correlations
        sorted_corrs = sorted(correlations, key=lambda x: x.correlation)
        lowest = sorted_corrs[0]
        highest = sorted_corrs[-1]

        return CorrelationMatrix(
            period_days=result["period_days"],
            correlations=correlations,
            diversification_score=result["diversification_score"],
            highest_correlation=highest,
            lowest_correlation=lowest,
=======
        return CorrelationMatrix(
            period_days=result["period_days"],
            correlations=correlations,
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")
