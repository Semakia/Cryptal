"""
Metrics router for cryptocurrency analytics endpoints.

Lit les métriques PRÉ-CALCULÉES depuis la couche Gold (tables gold_volatility,
gold_sharpe, gold_drawdown, gold_correlation_matrix), matérialisées par le DAG
(tâche build_gold). Plus aucun calcul à la volée ici : l'API ne fait que servir
ce que le batch a produit.

Le paramètre `period` est conservé pour compatibilité mais n'est plus utilisé
pour filtrer : la couche Gold contient une seule fenêtre pré-calculée, dont la
valeur réelle est renvoyée dans le champ `period_days`.
"""
import logging
import sys
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from database import _gold_cursor  # noqa: E402
from models import (  # noqa: E402
    CorrelationMatrix,
    CorrelationPair,
    DrawdownMetrics,
    SharpeMetrics,
    VolatilityMetrics,
)

router = APIRouter(prefix="/metrics", tags=["Metrics"])

# Cryptocurrencies to exclude from all endpoints
EXCLUDED_CRYPTOS = ["ripple", "tether"]


def _fetch_gold(query: str, params: tuple = ()):
    """Exécute une requête de lecture sur la base Gold et renvoie les lignes."""
    conn, cur = _gold_cursor()
    try:
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────── VOLATILITY ────────────────────────────────
@router.get("/volatility", response_model=List[VolatilityMetrics])
async def get_volatility_all(
    period: int = Query(365, ge=1, le=3650, description="Ignoré (Gold pré-calculé)"),
):
    """Volatilité pré-calculée pour toutes les cryptos (source: gold_volatility)."""
    rows = _fetch_gold(
        """
        SELECT coin_id, period_days, data_points, mean_price,
               period_volatility, annualized_volatility
        FROM gold_volatility
        WHERE coin_id NOT IN %s
        ORDER BY coin_id
        """,
        (tuple(EXCLUDED_CRYPTOS),),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="No volatility data in gold layer")
    return [VolatilityMetrics(**row) for row in rows]


@router.get("/volatility/{crypto_id}", response_model=VolatilityMetrics)
async def get_volatility(
    crypto_id: str,
    period: int = Query(365, ge=1, le=3650, description="Ignoré (Gold pré-calculé)"),
):
    """Volatilité pré-calculée pour une crypto (source: gold_volatility)."""
    rows = _fetch_gold(
        """
        SELECT coin_id, period_days, data_points, mean_price,
               period_volatility, annualized_volatility
        FROM gold_volatility WHERE coin_id = %s
        """,
        (crypto_id,),
    )
    if not rows:
        raise HTTPException(
            status_code=404, detail=f"No volatility data for {crypto_id}"
        )
    return VolatilityMetrics(**rows[0])


# ───────────────────────────────── SHARPE ──────────────────────────────────
@router.get("/sharpe", response_model=List[SharpeMetrics])
async def get_sharpe_all(
    period: int = Query(365, ge=1, le=3650, description="Ignoré (Gold pré-calculé)"),
    risk_free_rate: float = Query(0.02, ge=0, le=0.2, description="Ignoré (Gold)"),
):
    """Sharpe pré-calculé pour toutes les cryptos (source: gold_sharpe)."""
    rows = _fetch_gold(
        """
        SELECT coin_id, period_days, data_points, total_return,
               annualized_return, annualized_volatility, sharpe_ratio,
               start_price, end_price
        FROM gold_sharpe
        WHERE coin_id NOT IN %s
        ORDER BY coin_id
        """,
        (tuple(EXCLUDED_CRYPTOS),),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="No sharpe data in gold layer")
    return [SharpeMetrics(**row) for row in rows]


@router.get("/sharpe/{crypto_id}", response_model=SharpeMetrics)
async def get_sharpe(
    crypto_id: str,
    period: int = Query(365, ge=1, le=3650, description="Ignoré (Gold pré-calculé)"),
    risk_free_rate: float = Query(0.02, ge=0, le=0.2, description="Ignoré (Gold)"),
):
    """Sharpe pré-calculé pour une crypto (source: gold_sharpe)."""
    rows = _fetch_gold(
        """
        SELECT coin_id, period_days, data_points, total_return,
               annualized_return, annualized_volatility, sharpe_ratio,
               start_price, end_price
        FROM gold_sharpe WHERE coin_id = %s
        """,
        (crypto_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail=f"No sharpe data for {crypto_id}")
    return SharpeMetrics(**rows[0])


# ──────────────────────────────── DRAWDOWN ─────────────────────────────────
@router.get("/drawdown", response_model=List[DrawdownMetrics])
async def get_drawdown_all(
    period: int = Query(365, ge=1, le=3650, description="Ignoré (Gold pré-calculé)"),
):
    """Max drawdown pré-calculé pour toutes les cryptos (source: gold_drawdown)."""
    rows = _fetch_gold(
        """
        SELECT coin_id, period_days, data_points, max_drawdown_pct,
               peak_price, trough_price, peak_date, trough_date
        FROM gold_drawdown
        WHERE coin_id NOT IN %s
        ORDER BY coin_id
        """,
        (tuple(EXCLUDED_CRYPTOS),),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="No drawdown data in gold layer")
    return [DrawdownMetrics(**row) for row in rows]


@router.get("/drawdown/{crypto_id}", response_model=DrawdownMetrics)
async def get_drawdown(
    crypto_id: str,
    period: int = Query(365, ge=1, le=3650, description="Ignoré (Gold pré-calculé)"),
):
    """Max drawdown pré-calculé pour une crypto (source: gold_drawdown)."""
    rows = _fetch_gold(
        """
        SELECT coin_id, period_days, data_points, max_drawdown_pct,
               peak_price, trough_price, peak_date, trough_date
        FROM gold_drawdown WHERE coin_id = %s
        """,
        (crypto_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail=f"No drawdown data for {crypto_id}")
    return DrawdownMetrics(**rows[0])


# ─────────────────────────────── CORRELATION ───────────────────────────────
@router.get("/correlation", response_model=CorrelationMatrix)
async def get_correlation_matrix(
    period: int = Query(365, ge=1, le=3650, description="Ignoré (Gold pré-calculé)"),
):
    """Matrice de corrélation pré-calculée (source: gold_correlation_matrix)."""
    rows = _fetch_gold(
        """
        SELECT crypto_1, crypto_2, correlation, period_days
        FROM gold_correlation_matrix
        ORDER BY correlation DESC
        """
    )
    if not rows:
        raise HTTPException(
            status_code=404, detail="No correlation data in gold layer"
        )
    return CorrelationMatrix(
        period_days=rows[0]["period_days"],
        correlations=[
            CorrelationPair(
                crypto_1=r["crypto_1"],
                crypto_2=r["crypto_2"],
                correlation=r["correlation"],
            )
            for r in rows
        ],
    )
