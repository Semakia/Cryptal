"""
Crypto Viz API - Main Application
==================================

FastAPI application for the Crypto Viz real-time cryptocurrency analytics platform.
Provides REST endpoints for price data, volatility metrics, Sharpe ratios,
drawdown analysis, correlation matrices, and P&L simulations.

Usage
-----
Run with uvicorn:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

API Documentation
-----------------
Interactive docs available at:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
"""

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import data, health, metrics, simulation

# ============================================================================
# Application Setup
# ============================================================================

app = FastAPI(
    title="Crypto Viz API",
    description=(
        "Real-time cryptocurrency analytics platform providing price data, "
        "volatility metrics, risk-adjusted returns, correlation analysis, "
        "and portfolio simulations."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ============================================================================
# CORS Configuration
# ============================================================================

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default port
        "http://localhost:5173",  # Vite default port
        "http://localhost:8080",  # Alternative frontend port
        "*",  # Allow all origins (use with caution in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ============================================================================
# Exception Handlers
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unexpected errors.

    Parameters
    ----------
    request : Request
        The request that caused the exception.
    exc : Exception
        The exception that was raised.

    Returns
    -------
    JSONResponse
        Error response with details.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
        },
    )


# ============================================================================
# Route Inclusion
# ============================================================================

# Include health and status routes (no prefix)
app.include_router(health.router)

# Include API routes with /api prefix
app.include_router(data.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(simulation.router, prefix="/api")

# ============================================================================
# Root Endpoint
# ============================================================================


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing API information.

    Returns
    -------
    dict
        API information and available endpoints.
    """
    return {
        "name": "CrypTal API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "data": {
                "cryptos": "/api/data/cryptos",
                "prices": "/api/data/prices",
                "latest_prices": "/api/data/prices/latest",
                "crypto_prices": "/api/data/prices/{crypto_id}",
            },
            "metrics": {
                "volatility_all": "/api/metrics/volatility",
                "volatility": "/api/metrics/volatility/{crypto_id}",
                "sharpe_all": "/api/metrics/sharpe",
                "sharpe": "/api/metrics/sharpe/{crypto_id}",
                "drawdown_all": "/api/metrics/drawdown",
                "drawdown": "/api/metrics/drawdown/{crypto_id}",
                "correlation": "/api/metrics/correlation",
            },
            "simulation": {
                "pnl": "POST /api/simulate/pnl",
                "compare": "/api/simulate/pnl/compare",
                "best_entry": "POST /api/simulate/best-entry",
                "best_entry_get": "/api/simulate/best-entry/{crypto_id}",
            },
        },
        "description": (
            "Real-time cryptocurrency analytics platform. "
            "Visit /docs for interactive API documentation."
        ),
    }


# ============================================================================
# Startup and Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """
    Startup event handler.
    Executed when the application starts.
    """
    print("=" * 80)
    print("🚀 Crypto Viz API Starting...")
    print("=" * 80)
    print(f"📅 Start Time: {datetime.utcnow().isoformat()}")
    print(f"📚 Documentation: http://localhost:8000/docs")
    print(f"🔍 ReDoc: http://localhost:8000/redoc")
    print("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler.
    Executed when the application shuts down.
    """
    print("=" * 80)
    print("🛑 Crypto Viz API Shutting Down...")
    print(f"📅 Shutdown Time: {datetime.utcnow().isoformat()}")
    print("=" * 80)


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
