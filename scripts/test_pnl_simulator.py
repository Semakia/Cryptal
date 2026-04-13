#!/usr/bin/env python3
"""
CLI to test the PnL Portfolio Simulator.
Usage examples:
  python test_pnl_simulator.py simulate bitcoin 1000 "2025-12-02 13:00:00"
  python test_pnl_simulator.py compare 1000 "2025-12-02 13:00:00"
  python test_pnl_simulator.py best bitcoin 1000
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from pipelines.transform.portfolio_simulator import PortfolioSimulator

# Load environment variables
env_path = Path(__file__).parent.parent / "src" / ".env"
load_dotenv(dotenv_path=env_path)


def get_db_config():
    """Get database configuration from environment."""
    return {
        "host": os.getenv("BRONZE_DB_HOST"),
        "dbname": os.getenv("BRONZE_DB_NAME"),
        "user": os.getenv("BRONZE_DB_USER"),
        "password": os.getenv("BRONZE_DB_PASSWORD"),
        "port": os.getenv("BRONZE_DB_PORT", "5432"),
    }


def format_currency(amount):
    """Format amount as currency."""
    return f"${amount:,.2f}"


def format_percentage(percentage):
    """Format percentage with color."""
    color = "\033[92m" if percentage >= 0 else "\033[91m"  # Green/Red
    reset = "\033[0m"
    sign = "+" if percentage >= 0 else ""
    return f"{color}{sign}{percentage:.2f}%{reset}"


def print_investment_result(result):
    """Pretty print investment result."""
    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
        return

    print("\n" + "=" * 80)
    print(f"📊 Investment Simulation: {result['coin_id'].upper()}")
    print("=" * 80)
    print(f"\n💰 Investment Details:")
    print(f"  Initial Investment:  {format_currency(result['investment_amount'])}")
    print(f"  Purchase Date:       {result['purchase_date']}")
    print(f"  Purchase Price:      {format_currency(result['purchase_price'])}")
    print(f"  Quantity Bought:     {result['quantity']:.8f} {result['coin_id'].upper()}")
    
    print(f"\n📈 Current Status:")
    print(f"  Sell Date:           {result['sell_date']}")
    print(f"  Current Price:       {format_currency(result['sell_price'])}")
    print(f"  Current Value:       {format_currency(result['current_value'])}")
    
    print(f"\n🎯 Profit & Loss:")
    pnl_color = "\033[92m" if result['pnl'] >= 0 else "\033[91m"
    reset = "\033[0m"
    print(f"  P&L:                 {pnl_color}{format_currency(result['pnl'])}{reset}")
    print(f"  ROI:                 {format_percentage(result['roi'])}")
    print("=" * 80 + "\n")


def cmd_simulate(args):
    """Simulate a single investment."""
    if len(args) < 3:
        print("Usage: simulate <coin_id> <amount> <purchase_date>")
        print("Example: simulate bitcoin 1000 '2025-12-02 13:00:00'")
        return

    coin_id = args[0]
    amount = float(args[1])
    purchase_date = datetime.strptime(args[2], "%Y-%m-%d %H:%M:%S")

    simulator = PortfolioSimulator(get_db_config())
    result = simulator.simulate_investment(coin_id, amount, purchase_date)
    simulator.close()

    print_investment_result(result)


def cmd_compare(args):
    """Compare investments across all available cryptos."""
    if len(args) < 2:
        print("Usage: compare <amount> <purchase_date>")
        print("Example: compare 1000 '2025-12-02 13:00:00'")
        return

    amount = float(args[0])
    purchase_date = datetime.strptime(args[1], "%Y-%m-%d %H:%M:%S")

    simulator = PortfolioSimulator(get_db_config())
    
    # Get available coins
    coins = simulator.get_available_coins()
    print(f"\n🔍 Comparing {len(coins)} cryptocurrencies...")
    
    results = simulator.compare_investments(coins, amount, purchase_date)
    simulator.close()

    if not results:
        print("❌ No results found")
        return

    print("\n" + "=" * 80)
    print("🏆 Investment Comparison (Ranked by P&L)")
    print("=" * 80)
    print(f"\n💰 Investment Amount: {format_currency(amount)}")
    print(f"📅 Purchase Date: {purchase_date}\n")

    for i, result in enumerate(results, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        print(f"{medal} {result['coin_id'].upper():12} | "
              f"Value: {format_currency(result['current_value']):>12} | "
              f"P&L: {format_currency(result['pnl']):>12} | "
              f"ROI: {format_percentage(result['roi']):>10}")

    print("\n" + "=" * 80)
    
    # Show best and worst
    best = results[0]
    worst = results[-1]
    print(f"\n🎯 Best Investment:  {best['coin_id'].upper()} with {format_percentage(best['roi'])}")
    print(f"📉 Worst Investment: {worst['coin_id'].upper()} with {format_percentage(worst['roi'])}\n")


def cmd_best(args):
    """Find best historical entry point."""
    if len(args) < 2:
        print("Usage: best <coin_id> <amount> [lookback_days]")
        print("Example: best bitcoin 1000 30")
        return

    coin_id = args[0]
    amount = float(args[1])
    lookback_days = int(args[2]) if len(args) > 2 else 30

    simulator = PortfolioSimulator(get_db_config())
    result = simulator.get_best_entry_point(coin_id, amount, lookback_days)
    simulator.close()

    if "error" in result:
        print(f"\n❌ Error: {result['error']}")
        return

    print("\n" + "=" * 80)
    print(f"🎯 Best Entry Point Analysis: {result['coin_id'].upper()}")
    print("=" * 80)
    print(f"\n🔍 Analysis Period: Last {lookback_days} days")
    print(f"💰 Investment Amount: {format_currency(result['investment_amount'])}")
    
    print(f"\n✅ Best Entry Point:")
    print(f"  Date:                {result['best_entry_date']}")
    print(f"  Entry Price:         {format_currency(result['best_entry_price'])}")
    print(f"  Quantity:            {result['quantity']:.8f} {result['coin_id'].upper()}")
    
    print(f"\n📈 If You Had Invested Then:")
    print(f"  Current Price:       {format_currency(result['current_price'])}")
    print(f"  Current Value:       {format_currency(result['current_value'])}")
    
    pnl_color = "\033[92m" if result['pnl'] >= 0 else "\033[91m"
    reset = "\033[0m"
    print(f"\n🎉 P&L:")
    print(f"  Profit/Loss:         {pnl_color}{format_currency(result['pnl'])}{reset}")
    print(f"  ROI:                 {format_percentage(result['pnl_percentage'])}")
    print("=" * 80 + "\n")


def cmd_list(args):
    """List available cryptocurrencies and their date ranges."""
    simulator = PortfolioSimulator(get_db_config())
    coins = simulator.get_available_coins()

    print("\n" + "=" * 80)
    print("📋 Available Cryptocurrencies")
    print("=" * 80 + "\n")

    for coin in coins:
        earliest, latest = simulator.get_date_range(coin)
        print(f"🪙 {coin:15} | Data from {earliest} to {latest}")

    simulator.close()
    print()


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("\n🚀 PnL Portfolio Simulator CLI\n")
        print("Commands:")
        print("  simulate <coin> <amount> <date>     - Simulate single investment")
        print("  compare <amount> <date>             - Compare all cryptos")
        print("  best <coin> <amount> [days]         - Find best entry point")
        print("  list                                - List available cryptos")
        print("\nExamples:")
        print("  python test_pnl_simulator.py simulate bitcoin 1000 '2025-12-02 13:00:00'")
        print("  python test_pnl_simulator.py compare 1000 '2025-12-02 13:00:00'")
        print("  python test_pnl_simulator.py best ethereum 5000 30")
        print("  python test_pnl_simulator.py list\n")
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "simulate": cmd_simulate,
        "compare": cmd_compare,
        "best": cmd_best,
        "list": cmd_list,
    }

    if command in commands:
        commands[command](args)
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: simulate, compare, best, list")


if __name__ == "__main__":
    main()
