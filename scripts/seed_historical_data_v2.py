#!/usr/bin/env python3
"""
Seed database with historical data - Version 2
Uses CoinGecko Demo API (free, no auth needed for basic endpoints)
"""
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import psycopg2
import requests
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / "src" / ".env"
load_dotenv(dotenv_path=env_path)

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
COINS = {
    "bitcoin": "btc",
    "ethereum": "eth", 
    "solana": "sol",
    "binancecoin": "bnb",
}
DAYS_TO_SEED = 30

DB_HOST = os.getenv("BRONZE_DB_HOST")
DB_NAME = os.getenv("BRONZE_DB_NAME")
DB_USER = os.getenv("BRONZE_DB_USER")
DB_PASSWORD = os.getenv("BRONZE_DB_PASSWORD")
DB_PORT = os.getenv("BRONZE_DB_PORT", "5432")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER,
        password=DB_PASSWORD, port=DB_PORT, sslmode="require"
    )

def fetch_simple_price_history(coin_id, days=30):
    """Fetch using simple price endpoint (no auth needed)"""
    print(f"Fetching {days} days for {coin_id} via simple method...")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Generate hourly timestamps for the past N days
    now = datetime.now()
    data_points = []
    
    for hours_ago in range(0, days * 24, 1):  # Every hour
        timestamp = now - timedelta(hours=hours_ago)
        
        # Call CoinGecko simple price
        try:
            url = f"{COINGECKO_BASE}/simple/price"
            params = {
                "ids": coin_id,
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_change": "true"
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if coin_id in data:
                    price = data[coin_id].get("usd")
                    market_cap = data[coin_id].get("usd_market_cap")
                    change_24h = data[coin_id].get("usd_24h_change")
                    
                    data_points.append({
                        "coin_id": coin_id,
                        "timestamp": timestamp,
                        "price_usd": price,
                        "market_cap": market_cap,
                        "change_24h": change_24h
                    })
                    
            time.sleep(1.2)  # Rate limit: max 50 calls/min
            
            if hours_ago % 24 == 0:
                print(f"  Progress: {hours_ago // 24}/{days} days")
                
        except Exception as e:
            print(f"  Warning at hour {hours_ago}: {e}")
            continue
    
    cur.close()
    conn.close()
    
    print(f"  ✓ Collected {len(data_points)} points")
    return data_points

def insert_data(conn, data_points):
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
                'coingecko', 'usd', point["coin_id"], point["price_usd"],
                None, None, point["change_24h"], point["market_cap"], point["timestamp"]
            ))
            inserted += cur.rowcount
        except:
            continue
    
    conn.commit()
    cur.close()
    return inserted

def main():
    print("=" * 60)
    print("Historical Data Seeder V2 (Simple Method)")
    print("=" * 60)
    print(f"Coins: {list(COINS.keys())}")
    print(f"Days: {DAYS_TO_SEED}")
    print(f"Note: This will take ~{DAYS_TO_SEED * 24 * len(COINS) * 1.2 / 60:.0f} minutes")
    
    response = input("\nThis is SLOW but works. Continue? (y/n): ")
    if response.lower() != 'y':
        return 0
    
    conn = get_db_connection()
    total = 0
    
    for coin_id in COINS.keys():
        points = fetch_simple_price_history(coin_id, DAYS_TO_SEED)
        if points:
            inserted = insert_data(conn, points)
            print(f"  ✓ Inserted {inserted} records for {coin_id}\n")
            total += inserted
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Complete! Inserted {total} total records")
    print(f"{'='*60}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
