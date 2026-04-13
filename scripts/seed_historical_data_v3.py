#!/usr/bin/env python3
"""
Seed database with 30 days of historical data using CryptoCompare API (free, no key needed)
"""
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import psycopg2
import requests
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / "src" / ".env"
load_dotenv(dotenv_path=env_path)

# CryptoCompare API (free, no key needed)
CRYPTOCOMPARE_BASE = "https://min-api.cryptocompare.com/data/v2"

COINS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "binancecoin": "BNB",
}

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

def fetch_historical_hourly(coin_id, symbol, limit=720):
    """
    Fetch hourly data from CryptoCompare (free API)
    limit=720 = 30 days of hourly data
    """
    url = f"{CRYPTOCOMPARE_BASE}/histohour"
    params = {
        "fsym": symbol,
        "tsym": "USD",
        "limit": limit
    }
    
    print(f"Fetching {limit} hours (~{limit//24} days) for {coin_id}...")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("Response") != "Success":
            print(f"  ✗ API error: {data.get('Message', 'Unknown error')}")
            return []
        
        candles = data.get("Data", {}).get("Data", [])
        
        result = []
        for i, candle in enumerate(candles):
            timestamp = datetime.fromtimestamp(candle["time"])
            price = candle["close"]
            volume = candle["volumeto"]
            
            # Calculate 24h change
            change_24h = None
            if i >= 24:
                price_24h_ago = candles[i-24]["close"]
                if price_24h_ago > 0:
                    change_24h = ((price - price_24h_ago) / price_24h_ago) * 100
            
            result.append({
                "coin_id": coin_id,
                "timestamp": timestamp,
                "price_usd": price,
                "market_cap": None,  # CryptoCompare doesn't provide this in hourly
                "change_24h": change_24h
            })
        
        print(f"  ✓ Fetched {len(result)} data points")
        return result
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []

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
                'cryptocompare', 'usd', point["coin_id"], point["price_usd"],
                None, None, point["change_24h"], point["market_cap"], point["timestamp"]
            ))
            inserted += cur.rowcount
        except Exception as e:
            continue
    
    conn.commit()
    cur.close()
    return inserted

def check_existing_data(conn):
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
        print("\nExisting data:")
        for row in results:
            crypto, count, first, last = row
            days = (last - first).days if first and last else 0
            print(f"  {crypto}: {count} records ({days} days)")
    else:
        print("\nNo existing data.")
    
    return results

def main():
    print("=" * 60)
    print("Historical Data Seeder - CryptoCompare API")
    print("=" * 60)
    print(f"Coins: {list(COINS.keys())}")
    print(f"Data: 30 days of hourly prices (~720 points per coin)")
    print(f"Source: CryptoCompare (free, no API key needed)")
    
    conn = get_db_connection()
    print("\n✓ Connected to database")
    
    check_existing_data(conn)
    
    response = input("\nProceed? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return 0
    
    print("\nFetching data...")
    total_inserted = 0
    
    for coin_id, symbol in COINS.items():
        data_points = fetch_historical_hourly(coin_id, symbol, limit=720)
        
        if data_points:
            print(f"  Inserting {len(data_points)} points...")
            inserted = insert_data(conn, data_points)
            print(f"  ✓ Inserted {inserted} new records\n")
            total_inserted += inserted
        
        time.sleep(0.5)  # Be nice to the API
    
    print("=" * 60)
    print(f"Complete! Inserted {total_inserted} records")
    print("=" * 60)
    
    check_existing_data(conn)
    
    print("\nTest endpoints:")
    print("  curl 'http://localhost:8000/api/metrics/volatility?period=7'")
    print("  curl 'http://localhost:8000/api/metrics/sharpe?period=30'")
    
    conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
