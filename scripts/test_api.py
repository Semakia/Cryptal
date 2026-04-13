#!/usr/bin/env python3
"""
Test script for Crypto Viz API endpoints.
Tests all available endpoints to ensure they're working correctly.

Usage:
    python scripts/test_api.py
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests

# API base URL
BASE_URL = "http://localhost:8000"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_test(name):
    """Print test name."""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}Testing: {name}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}")


def print_success(message):
    """Print success message."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print error message."""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    """Print info message."""
    print(f"{YELLOW}ℹ {message}{RESET}")


def test_health_check():
    """Test health check endpoint."""
    print_test("Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health")

        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data['status']}")
            print_info(f"Database: {data['database']}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False


def test_status():
    """Test status endpoint."""
    print_test("System Status")

    try:
        response = requests.get(f"{BASE_URL}/status")

        if response.status_code == 200:
            data = response.json()
            print_success("Status check passed")
            print_info(f"Database connected: {data['database_connected']}")
            print_info(f"Total data points: {data['total_data_points']}")
            print_info(f"Cryptocurrencies: {', '.join(data['cryptocurrencies'])}")
            if data["last_data_collection"]:
                print_info(f"Last collection: {data['last_data_collection']}")
            return True
        else:
            print_error(f"Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Status check error: {str(e)}")
        return False


def test_get_cryptos():
    """Test get cryptocurrencies endpoint."""
    print_test("Get Cryptocurrencies")

    try:
        response = requests.get(f"{BASE_URL}/api/data/cryptos")

        if response.status_code == 200:
            data = response.json()
            print_success(f"Found {len(data)} cryptocurrencies")
            for crypto in data:
                print_info(
                    f"  {crypto['coin_id']}: {crypto['data_points']} data points "
                    f"({crypto['earliest_date']} to {crypto['latest_date']})"
                )
            return data
        else:
            print_error(f"Get cryptos failed: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Get cryptos error: {str(e)}")
        return []


def test_latest_prices():
    """Test get latest prices endpoint."""
    print_test("Get Latest Prices")

    try:
        response = requests.get(f"{BASE_URL}/api/data/prices/latest")

        if response.status_code == 200:
            result = response.json()
            print_success(f"Got {result['count']} latest prices")
            for price in result["data"]:
                print_info(
                    f"  {price['coin_id']}: ${price['price_usd']:,.2f} "
                    f"({price['change_24h']:+.2f}% 24h)"
                )
            return True
        else:
            print_error(f"Get latest prices failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get latest prices error: {str(e)}")
        return False


def test_get_prices(crypto="bitcoin", days=7):
    """Test get historical prices endpoint."""
    print_test(f"Get Historical Prices ({crypto}, {days} days)")

    try:
        response = requests.get(
            f"{BASE_URL}/api/data/prices/{crypto}", params={"days": days, "limit": 100}
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Got {len(data)} price points")
            if data:
                print_info(
                    f"  Latest: ${data[0]['price_usd']:,.2f} at {data[0]['timestamp']}"
                )
                print_info(
                    f"  Oldest: ${data[-1]['price_usd']:,.2f} at {data[-1]['timestamp']}"
                )
            return True
        else:
            print_error(f"Get prices failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get prices error: {str(e)}")
        return False


def test_volatility(crypto="bitcoin", period=7):
    """Test volatility metrics endpoint."""
    print_test(f"Volatility Metrics ({crypto}, {period} days)")

    try:
        response = requests.get(
            f"{BASE_URL}/api/metrics/volatility/{crypto}", params={"period": period}
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Volatility calculated")
            print_info(f"  Mean price: ${data['mean_price']:,.2f}")
            print_info(f"  Std deviation: ${data['std_dev']:,.2f}")
            print_info(f"  CV: {data['coefficient_of_variation']:.2f}%")
            print_info(f"  VaR 95%: ${data['var_95']:,.2f}")
            print_info(
                f"  Range: ${data['min_price']:,.2f} - ${data['max_price']:,.2f}"
            )
            return True
        else:
            print_error(f"Volatility failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Volatility error: {str(e)}")
        return False


def test_sharpe(crypto="bitcoin", period=30):
    """Test Sharpe ratio endpoint."""
    print_test(f"Sharpe Ratio ({crypto}, {period} days)")

    try:
        response = requests.get(
            f"{BASE_URL}/api/metrics/sharpe/{crypto}", params={"period": period}
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Sharpe ratio calculated")
            print_info(f"  Total return: {data['total_return']:.2f}%")
            print_info(f"  Annualized return: {data['annualized_return']:.2f}%")
            print_info(f"  Annualized volatility: {data['annualized_volatility']:.2f}%")
            print_info(f"  Sharpe ratio: {data['sharpe_ratio']:.2f}")
            print_info(f"  Sortino ratio: {data['sortino_ratio']:.2f}")
            return True
        else:
            print_error(f"Sharpe failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Sharpe error: {str(e)}")
        return False


def test_drawdown(crypto="bitcoin", period=30):
    """Test drawdown metrics endpoint."""
    print_test(f"Drawdown Metrics ({crypto}, {period} days)")

    try:
        response = requests.get(
            f"{BASE_URL}/api/metrics/drawdown/{crypto}", params={"period": period}
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Drawdown calculated")
            print_info(f"  Max drawdown: {data['max_drawdown_pct']:.2f}%")
            print_info(f"  Current drawdown: {data['current_drawdown_pct']:.2f}%")
            print_info(f"  Underwater: {data['underwater_pct']:.2f}%")
            print_info(f"  Peak: ${data['peak_price']:,.2f} at {data['peak_date']}")
            print_info(
                f"  Trough: ${data['trough_price']:,.2f} at {data['trough_date']}"
            )
            return True
        else:
            print_error(f"Drawdown failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Drawdown error: {str(e)}")
        return False


def test_correlation(period=30):
    """Test correlation matrix endpoint."""
    print_test(f"Correlation Matrix ({period} days)")

    try:
        response = requests.get(
            f"{BASE_URL}/api/metrics/correlation", params={"period": period}
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Correlation matrix calculated")
            print_info(f"  Diversification score: {data['diversification_score']:.2f}")
            print_info(
                f"  Highest correlation: {data['highest_correlation']['crypto_1']} - "
                f"{data['highest_correlation']['crypto_2']}: "
                f"{data['highest_correlation']['correlation']:.3f}"
            )
            print_info(
                f"  Lowest correlation: {data['lowest_correlation']['crypto_1']} - "
                f"{data['lowest_correlation']['crypto_2']}: "
                f"{data['lowest_correlation']['correlation']:.3f}"
            )
            print_info(f"  Total pairs: {len(data['correlations'])}")
            return True
        else:
            print_error(f"Correlation failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Correlation error: {str(e)}")
        return False


def test_pnl_simulation(crypto="bitcoin", amount=1000.0):
    """Test P&L simulation endpoint."""
    print_test(f"P&L Simulation ({crypto}, ${amount})")

    # Use a date from 7 days ago
    purchase_date = (datetime.utcnow() - timedelta(days=7)).isoformat()

    try:
        response = requests.post(
            f"{BASE_URL}/api/simulate/pnl",
            json={"crypto": crypto, "amount": amount, "purchase_date": purchase_date},
        )

        if response.status_code == 200:
            data = response.json()
            print_success("P&L simulation completed")
            print_info(f"  Investment: ${data['investment_amount']:,.2f}")
            print_info(f"  Purchase price: ${data['purchase_price']:,.2f}")
            print_info(f"  Quantity: {data['quantity']:.8f}")
            print_info(f"  Current price: ${data['sell_price']:,.2f}")
            print_info(f"  Current value: ${data['current_value']:,.2f}")

            pnl_color = GREEN if data["pnl"] >= 0 else RED
            print(f"{pnl_color}  P&L: ${data['pnl']:,.2f} ({data['roi']:+.2f}%){RESET}")
            return True
        else:
            print_error(
                f"P&L simulation failed: {response.status_code} - {response.text}"
            )
            return False
    except Exception as e:
        print_error(f"P&L simulation error: {str(e)}")
        return False


def test_best_entry_point(crypto="bitcoin", amount=1000.0, lookback=30):
    """Test best entry point endpoint."""
    print_test(f"Best Entry Point ({crypto}, ${amount}, {lookback} days)")

    try:
        response = requests.get(
            f"{BASE_URL}/api/simulate/best-entry/{crypto}",
            params={"amount": amount, "lookback_days": lookback},
        )

        if response.status_code == 200:
            data = response.json()
            print_success("Best entry point found")
            print_info(f"  Best entry date: {data['best_entry_date']}")
            print_info(f"  Entry price: ${data['best_entry_price']:,.2f}")
            print_info(f"  Current price: ${data['current_price']:,.2f}")
            print_info(f"  Quantity: {data['quantity']:.8f}")
            print_info(f"  Current value: ${data['current_value']:,.2f}")

            pnl_color = GREEN if data["pnl"] >= 0 else RED
            print(
                f"{pnl_color}  P&L: ${data['pnl']:,.2f} ({data['pnl_percentage']:+.2f}%){RESET}"
            )
            return True
        else:
            print_error(
                f"Best entry point failed: {response.status_code} - {response.text}"
            )
            return False
    except Exception as e:
        print_error(f"Best entry point error: {str(e)}")
        return False


def main():
    """Run all API tests."""
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}🧪 Crypto Viz API Test Suite{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}")
    print(f"{YELLOW}Testing API at: {BASE_URL}{RESET}")

    results = {}

    # Run tests
    results["Health Check"] = test_health_check()
    results["Status"] = test_status()

    cryptos = test_get_cryptos()
    results["Get Cryptos"] = len(cryptos) > 0

    results["Latest Prices"] = test_latest_prices()

    # Use first available crypto for testing
    test_crypto = cryptos[0]["coin_id"] if cryptos else "bitcoin"

    results["Historical Prices"] = test_get_prices(test_crypto, days=7)
    results["Volatility"] = test_volatility(test_crypto, period=7)
    results["Sharpe Ratio"] = test_sharpe(test_crypto, period=30)
    results["Drawdown"] = test_drawdown(test_crypto, period=30)
    results["Correlation"] = test_correlation(period=30)
    results["P&L Simulation"] = test_pnl_simulation(test_crypto, amount=1000.0)
    results["Best Entry Point"] = test_best_entry_point(
        test_crypto, amount=1000.0, lookback=30
    )

    # Summary
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}📊 Test Summary{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        if result:
            print(f"{GREEN}✓{RESET} {test_name}")
        else:
            print(f"{RED}✗{RESET} {test_name}")

    print(f"\n{BLUE}{'=' * 80}{RESET}")

    if passed == total:
        print(f"{GREEN}🎉 All tests passed! ({passed}/{total}){RESET}")
        sys.exit(0)
    else:
        print(f"{YELLOW}⚠ {passed}/{total} tests passed{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
