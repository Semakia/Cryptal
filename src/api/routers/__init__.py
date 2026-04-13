"""
API Routers Package
===================

Contains all API route handlers organized by domain:
- data: Raw cryptocurrency price data
- metrics: Analytics and metrics (volatility, Sharpe, drawdown, correlation)
- simulation: Portfolio simulations and P&L calculations
- health: Health checks and system status
"""

from . import data, health, metrics, simulation

__all__ = ["data", "health", "metrics", "simulation"]
