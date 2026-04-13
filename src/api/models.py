"""
Pydantic models for API request and response schemas.
"""

from datetime import datetime
<<<<<<< HEAD
from typing import List, Optional

from pydantic import BaseModel, Field
=======
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1

# ============================================================================
# Request Models
# ============================================================================


class PnLSimulationRequest(BaseModel):
    """Request model for P&L simulation."""

    crypto: str = Field(..., description="Cryptocurrency ID (e.g., 'bitcoin')")
    amount: float = Field(..., gt=0, description="Investment amount in USD")
    purchase_date: datetime = Field(..., description="Purchase date and time")

    class Config:
        json_schema_extra = {
            "example": {
                "crypto": "bitcoin",
                "amount": 1000.0,
                "purchase_date": "2024-01-01T12:00:00",
            }
        }


class BestEntryPointRequest(BaseModel):
    """Request model for finding best entry point."""

    crypto: str = Field(..., description="Cryptocurrency ID")
    amount: float = Field(..., gt=0, description="Investment amount in USD")
    lookback_days: int = Field(30, ge=1, le=365, description="Days to look back")

    class Config:
        json_schema_extra = {
            "example": {"crypto": "ethereum", "amount": 5000.0, "lookback_days": 30}
        }


# ============================================================================
# Response Models
# ============================================================================


class CryptoInfo(BaseModel):
    """Basic cryptocurrency information."""

    coin_id: str
    data_points: int
    earliest_date: Optional[datetime] = None
    latest_date: Optional[datetime] = None


class PriceData(BaseModel):
    """Price data point."""

    id: int
    coin_id: str
    price_usd: float
    price_eur: Optional[float] = None
    price_gbp: Optional[float] = None
    change_24h: Optional[float] = None
    market_cap: Optional[int] = None
    timestamp: datetime

<<<<<<< HEAD
=======
    @field_validator("market_cap", mode="before")
    @classmethod
    def convert_market_cap(cls, v):
        if v is None:
            return None
        if isinstance(v, Decimal):
            return int(v)
        return v

>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1

class LatestPrices(BaseModel):
    """Latest prices for all cryptocurrencies."""

    data: List[PriceData]
    count: int
    last_update: Optional[datetime] = None


class VolatilityMetrics(BaseModel):
    """Volatility metrics for a cryptocurrency."""

    coin_id: str
    period_days: int
    data_points: int
    mean_price: float
<<<<<<< HEAD
    std_dev: float  # Period volatility (%)
    annualized_volatility: Optional[float] = None  # Annualized volatility (%)
    variance: float
    coefficient_of_variation: float
    var_95: float
    min_price: float
    max_price: float
    price_range: float
=======
    period_volatility: float  # Actual volatility for the period (%)
    annualized_volatility: float  # Annualized volatility (%)
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1


class SharpeMetrics(BaseModel):
    """Sharpe ratio and related metrics."""

    coin_id: str
    period_days: int
    data_points: int
    total_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
<<<<<<< HEAD
    sortino_ratio: float
=======
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
    start_price: float
    end_price: float


class DrawdownPeriod(BaseModel):
    """Single drawdown period data point."""

    start: str
    drawdown: float


class DrawdownMetrics(BaseModel):
    """Drawdown metrics for a cryptocurrency."""

    coin_id: str
    period_days: int
    data_points: int
    max_drawdown_pct: float
    max_drawdown_value: float
<<<<<<< HEAD
    current_drawdown_pct: float
    underwater_pct: float
    peak_price: float
    trough_price: float
    current_price: float
    peak_date: Optional[datetime] = None
    trough_date: Optional[datetime] = None
    drawdown_periods: List[DrawdownPeriod] = []
=======
    peak_price: float
    trough_price: float
    peak_date: Optional[datetime] = None
    trough_date: Optional[datetime] = None
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1


class CorrelationPair(BaseModel):
    """Correlation between two cryptocurrencies."""

    crypto_1: str
    crypto_2: str
    correlation: float


class CorrelationMatrix(BaseModel):
    """Full correlation matrix."""

    period_days: int
    correlations: List[CorrelationPair]
<<<<<<< HEAD
    diversification_score: float
    highest_correlation: CorrelationPair
    lowest_correlation: CorrelationPair
=======
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1


class PnLSimulationResult(BaseModel):
    """Result of a P&L simulation."""

    coin_id: str
    investment_amount: float
    purchase_date: datetime
    purchase_price: float
    quantity: float
<<<<<<< HEAD
    sell_date: datetime
=======
    sell_date: Optional[datetime] = None  # ✅ FIX
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
    sell_price: float
    current_value: float
    pnl: float
    roi: float


class BestEntryPointResult(BaseModel):
    """Result of best entry point analysis."""

    coin_id: str
    investment_amount: float
    lookback_days: int
    best_entry_date: datetime
    best_entry_price: float
    quantity: float
    current_price: float
    current_value: float
    pnl: float
    pnl_percentage: float


class HealthCheck(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
    database: str


class StatusResponse(BaseModel):
    """System status response."""

    status: str
    database_connected: bool
    total_data_points: int
    cryptocurrencies: List[str]
    last_data_collection: Optional[datetime] = None
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
<<<<<<< HEAD
    timestamp: datetime = Field(default_factory=datetime.utcnow)
=======
    timestamp: datetime = Field(default_factory=datetime.utcnow)
>>>>>>> abf4febebab2e997586d0832b94edec22db5c0c1
