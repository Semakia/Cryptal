"""
Health and status router for system monitoring endpoints.
Provides health checks and system status information.
"""

from datetime import datetime

from database import DatabaseConnection, get_db
from fastapi import APIRouter, Depends, HTTPException
from models import HealthCheck, StatusResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheck)
async def health_check(db: DatabaseConnection = Depends(get_db)):
    """
    Basic health check endpoint.

    Verifies that the API is running and can connect to the database.

    Returns
    -------
    HealthCheck
        Health status with timestamp.
    """
    try:
        # Test database connection
        cursor = db.get_cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()

        return HealthCheck(
            status="healthy",
            timestamp=datetime.utcnow(),
            database="connected",
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: Database connection failed - {str(e)}",
        )


@router.get("/status", response_model=StatusResponse)
async def get_status(db: DatabaseConnection = Depends(get_db)):
    """
    Get detailed system status information.

    Provides information about database connection, data collection status,
    and tracked cryptocurrencies.

    Returns
    -------
    StatusResponse
        Detailed system status including data statistics.
    """
    try:
        cursor = db.get_cursor()

        # Check database connection
        cursor.execute("SELECT 1")
        db_connected = cursor.fetchone() is not None

        # Get total data points
        cursor.execute("SELECT COUNT(*) as count FROM crypto_prices")
        total_data_points = cursor.fetchone()["count"]

        # Get list of cryptocurrencies
        cursor.execute("SELECT DISTINCT coin_id FROM crypto_prices ORDER BY coin_id")
        cryptocurrencies = [row["coin_id"] for row in cursor.fetchall()]

        # Get last data collection timestamp
        cursor.execute("SELECT MAX(timestamp) as last_update FROM crypto_prices")
        result = cursor.fetchone()
        last_data_collection = result["last_update"] if result else None

        cursor.close()

        return StatusResponse(
            status="operational",
            database_connected=db_connected,
            total_data_points=total_data_points,
            cryptocurrencies=cryptocurrencies,
            last_data_collection=last_data_collection,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving status: {str(e)}"
        )
