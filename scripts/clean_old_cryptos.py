#!/usr/bin/env python3
"""
Script to clean old crypto data (Ripple and Tether) from Neon DB.
"""

import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / "src" / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("BRONZE_DB_HOST")
DB_NAME = os.getenv("BRONZE_DB_NAME")
DB_USER = os.getenv("BRONZE_DB_USER")
DB_PASSWORD = os.getenv("BRONZE_DB_PASSWORD")
DB_PORT = os.getenv("BRONZE_DB_PORT", "5432")


def connect_db():
    """Connect to Neon DB."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode="require",
        )
        return conn
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None


def count_records(conn, coin_id):
    """Count records for a specific coin."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM crypto_prices WHERE coin_id = %s;",
        (coin_id,)
    )
    count = cursor.fetchone()[0]
    cursor.close()
    return count


def delete_records(conn, coin_id):
    """Delete all records for a specific coin."""
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM crypto_prices WHERE coin_id = %s;",
        (coin_id,)
    )
    deleted = cursor.rowcount
    conn.commit()
    cursor.close()
    return deleted


def main():
    """Main cleanup function."""
    print("\n" + "=" * 80)
    print("🧹 Cleaning Old Crypto Data from Neon DB")
    print("=" * 80)
    
    # Connect to DB
    conn = connect_db()
    if not conn:
        return
    
    coins_to_remove = ["ripple", "tether"]
    
    print("\n📊 Current state:")
    total_before = 0
    for coin in coins_to_remove:
        count = count_records(conn, coin)
        total_before += count
        print(f"  {coin:15} : {count:5} records")
    
    # Ask for confirmation
    print(f"\n⚠️  About to delete {total_before} records for {', '.join(coins_to_remove)}")
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response != "yes":
        print("\n❌ Cleanup cancelled.")
        conn.close()
        return
    
    # Delete records
    print("\n🗑️  Deleting records...")
    total_deleted = 0
    for coin in coins_to_remove:
        deleted = delete_records(conn, coin)
        total_deleted += deleted
        print(f"  ✅ Deleted {deleted} records for {coin}")
    
    # Show final state
    print("\n📊 Remaining cryptocurrencies:")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT coin_id, COUNT(*) as count, 
               MIN(timestamp) as first, 
               MAX(timestamp) as last
        FROM crypto_prices
        GROUP BY coin_id
        ORDER BY coin_id;
    """)
    
    for row in cursor.fetchall():
        print(f"  🪙 {row[0]:15} : {row[1]:5} records (from {row[2]} to {row[3]})")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print(f"✅ Cleanup complete! Deleted {total_deleted} records.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
