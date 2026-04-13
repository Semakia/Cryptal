#!/usr/bin/env python3
"""
Script to test and verify data parsing in Neon DB.
This script checks:
- Connection to Neon DB
- Data structure and types
- Sample data quality
- Statistics on collected data
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# Load environment variables from src/.env
env_path = Path(__file__).parent.parent / "src" / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("BRONZE_DB_HOST")
DB_NAME = os.getenv("BRONZE_DB_NAME")
DB_USER = os.getenv("BRONZE_DB_USER")
DB_PASSWORD = os.getenv("BRONZE_DB_PASSWORD")
DB_PORT = os.getenv("BRONZE_DB_PORT", "5432")


def test_connection():
    """Test connection to Neon DB."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode="require",
        )
        print("✅ Connection to Neon DB successful!")
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None


def check_table_structure(conn):
    """Check the structure of crypto_prices table."""
    print("\n📋 Table Structure:")
    print("-" * 80)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'crypto_prices'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]:20} | {col[1]:20} | Nullable: {col[2]}")
        cursor.close()
    except Exception as e:
        print(f"❌ Error checking table structure: {e}")


def get_data_statistics(conn):
    """Get statistics on collected data."""
    print("\n📊 Data Statistics:")
    print("-" * 80)
    try:
        cursor = conn.cursor()

        # Total count
        cursor.execute("SELECT COUNT(*) FROM crypto_prices;")
        total = cursor.fetchone()[0]
        print(f"  Total records: {total}")

        # Count by coin
        cursor.execute("""
            SELECT coin_id, COUNT(*) as count
            FROM crypto_prices
            GROUP BY coin_id
            ORDER BY count DESC;
        """)
        print("\n  Records by coin:")
        for row in cursor.fetchall():
            print(f"    {row[0]:15} : {row[1]:5} records")

        # Time range
        cursor.execute("""
            SELECT
                MIN(timestamp) as first_record,
                MAX(timestamp) as last_record
            FROM crypto_prices;
        """)
        time_range = cursor.fetchone()
        if time_range[0]:
            print(f"\n  First record: {time_range[0]}")
            print(f"  Last record:  {time_range[1]}")

        # Check for null values
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(price_usd) as has_price_usd,
                COUNT(change_24h) as has_change_24h,
                COUNT(market_cap) as has_market_cap
            FROM crypto_prices;
        """)
        nulls = cursor.fetchone()
        print(f"\n  Data completeness:")
        print(
            f"    price_usd:  {nulls[1]:5} / {nulls[0]:5} ({100 * nulls[1] / nulls[0]:.1f}%)"
        )
        print(
            f"    change_24h: {nulls[2]:5} / {nulls[0]:5} ({100 * nulls[2] / nulls[0]:.1f}%)"
        )
        print(
            f"    market_cap: {nulls[3]:5} / {nulls[0]:5} ({100 * nulls[3] / nulls[0]:.1f}%)"
        )

        cursor.close()
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")


def show_sample_data(conn, limit=5):
    """Show sample data from the database."""
    print(f"\n📝 Sample Data (last {limit} records):")
    print("-" * 80)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                coin_id,
                price_usd,
                change_24h,
                market_cap,
                timestamp
            FROM crypto_prices
            ORDER BY timestamp DESC
            LIMIT %s;
        """,
            (limit,),
        )

        records = cursor.fetchall()
        for record in records:
            print(f"\n  🪙 {record[0].upper()}")
            print(f"     Price (USD):    ${record[1]:,.2f}")
            print(
                f"     Change 24h:     {record[2]:+.2f}%"
                if record[2]
                else "     Change 24h:     N/A"
            )
            print(
                f"     Market Cap:     ${record[3]:,.0f}"
                if record[3]
                else "     Market Cap:     N/A"
            )
            print(f"     Timestamp:      {record[4]}")

        cursor.close()
    except Exception as e:
        print(f"❌ Error showing sample data: {e}")


def check_data_freshness(conn):
    """Check if data is being updated regularly."""
    print("\n⏰ Data Freshness Check:")
    print("-" * 80)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                coin_id,
                MAX(timestamp) as last_update,
                EXTRACT(EPOCH FROM (NOW() - MAX(timestamp))) as seconds_ago
            FROM crypto_prices
            GROUP BY coin_id
            ORDER BY coin_id;
        """)

        for row in cursor.fetchall():
            seconds_ago = int(row[2])
            status = "✅" if seconds_ago < 120 else "⚠️"
            print(f"  {status} {row[0]:15} : Last update {seconds_ago}s ago ({row[1]})")

        cursor.close()
    except Exception as e:
        print(f"❌ Error checking freshness: {e}")


def main():
    """Main function to run all tests."""
    print("\n" + "=" * 80)
    print("🧪 NEON DB DATA PARSING TEST")
    print("=" * 80)

    # Test connection
    conn = test_connection()
    if not conn:
        return

    # Run all checks
    check_table_structure(conn)
    get_data_statistics(conn)
    show_sample_data(conn)
    check_data_freshness(conn)

    # Close connection
    conn.close()
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
