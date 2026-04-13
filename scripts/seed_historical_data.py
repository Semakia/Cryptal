#!/usr/bin/env python3
"""
Seed the database with historical cryptocurrency data from CoinGecko.
"""
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import psycopg2
import requests
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / "src" / ".env"
load_dotenv(dotenv_path=env_path)

# Configuration
COINGECKO_BASE = "https://api.coingecko.com/api/v3"
COINS = ["bitcoin", "ethereum", "solana", "binancecoin", "hyperliquid"]
DAYS_TO_SEED = 7
VS_CURRENCY = "usd"

DB_HOST = os.getenv("BRONZE_DB_HOST")
DB_NAME = os.getenv("BRONZE_DB_NAME")
DB_USER = os.getenv("BRONZE_DB_USER")
DB_PASSWORD = os.getenv("BRONZE_DB_PASSWORD")
DB_PORT = os.getenv("BRONZE_DB_PORT", "5432")

def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        sslmode="require"
    )

def fetch_historical_data(coin_id, days=30):
    """Fetch historical market data from CoinGecko."""
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": VS_CURRENCY,
        "days": days,
        "interval": "hourly"
    }
    
    print(f"Fetching {days} days of data for {coin_id}...")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        prices = data.get("prices", [])
        market_caps = data.get("market_caps", [])
        
        result = []
        for i in range(len(prices)):
            timestamp_ms = prices[i][0]
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
            
            # Calculate 24h change
            change_24h = None
            if i >= 24:
                price_24h_ago = prices[i-24][1]
                current_price = prices[i][1]
                if price_24h_ago > 0:
                    change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
            
            result.append({
                "coin_id": coin_id,
                "timestamp": timestamp,
                "price_usd": prices[i][1],
                "market_cap": market_caps[i][1] if i < len(market_caps) else None,
                "change_24h": change_24h,
            })
        
        print(f"  ✓ Fetched {len(result)} data points for {coin_id}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error fetching {coin_id}: {e}")
        return []

def insert_data(conn, data_points):
    """Insert historical data into the database."""
    cur = conn.cursor()
    
    insert_query = """
        INSERT INTO crypto_prices 
        (source, currency, coin_id, price_usd, price_eur, price_gbp, change_24h, market_cap, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    
    inserted = 0
    for point in data_points:
        try:
            cur.execute(insert_query, (
                'coingecko',
                'usd',
                point["coin_id"],
                point["price_usd"],
                None,
                None,
                point["change_24h"],
                point["market_cap"],
                point["timestamp"]
            ))
            inserted += cur.rowcount
        except Exception as e:
            continue
    
    conn.commit()
    cur.close()
    
    return inserted

def check_existing_data(conn):
    """Check how much data already exists."""
    cur = conn.cursor()
    cur.execute("""
        SELECT coin_id, COUNT(*) as count,
               MIN(timestamp) as first,
               MAX(timestamp) as last
        FROM crypto_prices
        GROUP BY coin_id
    """)
    
    results = cur.fetchall()
    cur.close()
    
    if results:
        print("\nExisting data in database:")
        for row in results:
            crypto, count, first, last = row
            days = (last - first).days if first and last else 0
            print(f"  {crypto}: {count} records ({days} days span)")
    else:
        print("\nNo existing data in database.")
    
    return results

def main():
    """Main seeding function."""
    print("=" * 60)
    print("Crypto Viz - Historical Data Seeder")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Coins: {', '.join(COINS)}")
    print(f"  Days to seed: {DAYS_TO_SEED}")
    print(f"  Data interval: hourly")
    print(f"  Expected points per coin: ~{DAYS_TO_SEED * 24}")
    
    # Connect to database
    print("\nConnecting to database...")
    try:
        conn = get_db_connection()
        print("  ✓ Connected")
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return 1
    
    # Check existing data
    check_existing_data(conn)
    
    # Confirm before proceeding
    print(f"\nThis will fetch and insert ~{DAYS_TO_SEED * 24 * len(COINS)} data points.")
    response = input("Proceed? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return 0
    
    # Fetch and insert data for each coin
    print("\nFetching historical data...")
    total_inserted = 0
    
    for coin in COINS:
        data_points = fetch_historical_data(coin, DAYS_TO_SEED)
        
        if data_points:
            print(f"  Inserting {len(data_points)} points for {coin}...")
            inserted = insert_data(conn, data_points)
            print(f"  ✓ Inserted {inserted} new records")
            total_inserted += inserted
        
        time.sleep(1.5)
    
    # Show final stats
    print("\n" + "=" * 60)
    print("Seeding complete!")
    print("=" * 60)
    print(f"\nTotal records inserted: {total_inserted}")
    
    check_existing_data(conn)
    
    print("\nYou can now test all analytics endpoints:")
    print("  - Volatility: /api/metrics/volatility?period=7")
    print("  - Sharpe: /api/metrics/sharpe?period=30")
    print("  - Drawdown: /api/metrics/drawdown?period=30")
    print("  - Correlation: /api/metrics/correlation?period=30")
    print("\nOr visit: http://localhost:8000/docs")
    
    conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
