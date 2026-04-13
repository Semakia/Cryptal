"""
Database connection module for the Crypto Viz API.
Handles PostgreSQL connection to Neon DB.
"""

import os
from typing import Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()


class DatabaseConnection:
    """Manages database connections for the API."""

    def __init__(self):
        """Initialize database connection parameters from environment."""
        self.host = os.getenv("BRONZE_DB_HOST")
        self.dbname = os.getenv("BRONZE_DB_NAME")
        self.user = os.getenv("BRONZE_DB_USER")
        self.password = os.getenv("BRONZE_DB_PASSWORD")
        self.port = os.getenv("BRONZE_DB_PORT", "5432")
        self._connection: Optional[psycopg2.extensions.connection] = None

    def get_connection(self):
        """
        Get a database connection.
        Creates a new connection if one doesn't exist.

        Returns
        -------
        psycopg2.connection
            Active database connection.
        """
        if self._connection is None or self._connection.closed:
            connection_string = (
                f"host={self.host} dbname={self.dbname} user={self.user} "
                f"password={self.password} port={self.port} sslmode=require"
            )
            self._connection = psycopg2.connect(connection_string)
        return self._connection

    def get_cursor(self, dict_cursor=True):
        """
        Get a database cursor.

        Parameters
        ----------
        dict_cursor : bool
            If True, returns a RealDictCursor (results as dictionaries).
            If False, returns a regular cursor.

        Returns
        -------
        cursor
            Database cursor.
        """
        conn = self.get_connection()
        if dict_cursor:
            return conn.cursor(cursor_factory=RealDictCursor)
        return conn.cursor()

    def close(self):
        """Close the database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def get_db_config():
    """
    Get database configuration as a dictionary.
    Used by analytics modules that expect this format.

    Returns
    -------
    dict
        Database configuration dictionary.
    """
    return {
        "host": os.getenv("BRONZE_DB_HOST"),
        "dbname": os.getenv("BRONZE_DB_NAME"),
        "user": os.getenv("BRONZE_DB_USER"),
        "password": os.getenv("BRONZE_DB_PASSWORD"),
        "port": os.getenv("BRONZE_DB_PORT", "5432"),
    }


# Global database instance
db = DatabaseConnection()


def get_db():
    """
    Dependency function for FastAPI endpoints.

    Yields
    ------
    DatabaseConnection
        Database connection instance.
    """
    try:
        yield db
    finally:
        # Connection is kept alive for performance
        # Close it manually when needed
        pass
