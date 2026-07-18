"""
Simulation router for P&L and investment simulation endpoints.
Provides portfolio simulation and best entry point analysis.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Query

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from database import DatabaseConnection, get_db, get_db_config
from models import (
    BestEntryPointRequest,
    BestEntryPointResult,
    PnLSimulationRequest,
    PnLSimulationResult,
)
from pipelines.transform.portfolio_simulator import PortfolioSimulator

router = APIRouter(prefix="/simulate", tags=["Simulation"])


@router.post("/pnl", response_model=PnLSimulationResult)
async def simulate_pnl(
    request: PnLSimulationRequest = Body(...),
):
    """
    Simulate a P&L (Profit and Loss) for a cryptocurrency investment.

    Given an investment amount and purchase date, calculates the current
    value and profit/loss based on the latest available price.

    Parameters
    ----------
    request : PnLSimulationRequest
        Simulation parameters including crypto ID, investment amount, and purchase date.

    Returns
    -------
    PnLSimulationResult
        Detailed P&L simulation result with ROI and current value.

    Examples
    --------
    Request body:
    ```json
    {
        "crypto": "bitcoin",
        "amount": 1000.0,
        "purchase_date": "2024-01-01T12:00:00"
    }
    ```
    """
    try:
        simulator = PortfolioSimulator(get_db_config())
        result = simulator.simulate_investment(
            request.crypto, request.amount, request.purchase_date
        )
        simulator.close()

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return PnLSimulationResult(
            coin_id=result["coin_id"],
            investment_amount=result["investment_amount"],
            purchase_date=result["purchase_date"],
            purchase_price=result["purchase_price"],
            quantity=result["quantity"],
            sell_date=(
                None
                if result.get("sell_date") in ("latest", "", None)
                else result["sell_date"]
            ),
            sell_price=result["sell_price"],
            current_value=result["current_value"],
            pnl=result["pnl"],
            roi=result["roi"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@router.post("/pnl/compare", response_model=List[PnLSimulationResult])
async def compare_investments(
    amount: float = Query(..., gt=0, description="Investment amount in USD"),
    purchase_date: datetime = Query(..., description="Purchase date and time"),
    db: DatabaseConnection = Depends(get_db),
):
    """
    Compare P&L across all available cryptocurrencies for the same investment.

    Simulates investing the same amount in each cryptocurrency at the same time
    and returns results sorted by P&L (best to worst).

    Parameters
    ----------
    amount : float
        Investment amount in USD.
    purchase_date : datetime
        Purchase date and time for all simulations.

    Returns
    -------
    List[PnLSimulationResult]
        List of simulation results sorted by P&L (descending).

    Examples
    --------
    GET /simulate/pnl/compare?amount=1000&purchase_date=2024-01-01T12:00:00
    """
    try:
        simulator = PortfolioSimulator(get_db_config())

        # Get all available coins
        cursor = db.get_cursor()
        cursor.execute("SELECT DISTINCT coin_id FROM crypto_prices ORDER BY coin_id")
        coins = [row["coin_id"] for row in cursor.fetchall()]
        cursor.close()

        if not coins:
            raise HTTPException(status_code=404, detail="No cryptocurrencies found")

        # Compare investments
        results = simulator.compare_investments(coins, amount, purchase_date)
        simulator.close()

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No data available for date {purchase_date}",
            )

        # Convert to response models
        return [
            PnLSimulationResult(
                coin_id=r["coin_id"],
                investment_amount=r["investment_amount"],
                purchase_date=r["purchase_date"],
                purchase_price=r["purchase_price"],
                quantity=r["quantity"],
                sell_date=(
                    None
                    if r.get("sell_date") in ("latest", "", None)
                    else r["sell_date"]
                ),
                sell_price=r["sell_price"],
                current_value=r["current_value"],
                pnl=r["pnl"],
                roi=r["roi"],
            )
            for r in results
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")


@router.post("/best-entry", response_model=BestEntryPointResult)
async def find_best_entry_point(
    request: BestEntryPointRequest = Body(...),
):
    """
    Find the best historical entry point for a cryptocurrency investment.

    Analyzes historical data to find the optimal purchase date that would
    have yielded the highest profit if held until now.

    Parameters
    ----------
    request : BestEntryPointRequest
        Parameters including crypto ID, investment amount, and lookback period.

    Returns
    -------
    BestEntryPointResult
        Best entry point analysis with optimal purchase date and projected P&L.

    Examples
    --------
    Request body:
    ```json
    {
        "crypto": "ethereum",
        "amount": 5000.0,
        "lookback_days": 30
    }
    ```
    """
    try:
        simulator = PortfolioSimulator(get_db_config())
        result = simulator.get_best_entry_point(
            request.crypto, request.amount, request.lookback_days
        )
        simulator.close()

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return BestEntryPointResult(
            coin_id=result["coin_id"],
            investment_amount=result["investment_amount"],
            lookback_days=request.lookback_days,
            best_entry_date=result["best_entry_date"],
            best_entry_price=result["best_entry_price"],
            quantity=result["quantity"],
            current_price=result["current_price"],
            current_value=result["current_value"],
            pnl=result["pnl"],
            pnl_percentage=result["pnl_percentage"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.get("/best-entry/{crypto_id}", response_model=BestEntryPointResult)
async def get_best_entry_point(
    crypto_id: str,
    amount: float = Query(..., gt=0, description="Investment amount in USD"),
    lookback_days: int = Query(
        30, ge=1, le=365, description="Days to look back for analysis"
    ),
):
    """
    Find the best historical entry point for a specific cryptocurrency.

    Alternative GET endpoint for finding the best entry point.

    Parameters
    ----------
    crypto_id : str
        Cryptocurrency ID (e.g., 'bitcoin', 'ethereum').
    amount : float
        Investment amount in USD.
    lookback_days : int, default=30
        Number of days to look back for optimal entry point.

    Returns
    -------
    BestEntryPointResult
        Best entry point analysis.

    Examples
    --------
    GET /simulate/best-entry/bitcoin?amount=1000&lookback_days=30
    """
    try:
        simulator = PortfolioSimulator(get_db_config())
        result = simulator.get_best_entry_point(crypto_id, amount, lookback_days)
        simulator.close()

        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])

        return BestEntryPointResult(
            coin_id=result["coin_id"],
            investment_amount=result["investment_amount"],
            lookback_days=lookback_days,
            best_entry_date=result["best_entry_date"],
            best_entry_price=result["best_entry_price"],
            quantity=result["quantity"],
            current_price=result["current_price"],
            current_value=result["current_value"],
            pnl=result["pnl"],
            pnl_percentage=result["pnl_percentage"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
