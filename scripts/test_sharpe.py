#!/usr/bin/env python3
"""
CLI to test the Sharpe Ratio Calculator.
Usage examples:
  python test_sharpe.py calculate bitcoin 30
  python test_sharpe.py compare 7
  python test_sharpe.py best 30
  python test_sharpe.py sortino ethereum 30
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from pipelines.transform.sharpe_calculator import SharpeCalculator

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
    if percentage >= 0:
        color = "\033[92m"  # Green
        sign = "+"
    else:
        color = "\033[91m"  # Red
        sign = ""
    reset = "\033[0m"
    return f"{color}{sign}{percentage:.2f}%{reset}"


def format_sharpe(sharpe):
    """Format Sharpe ratio with color."""
    if sharpe >= 2:
        color = "\033[92m"  # Green
    elif sharpe >= 1:
        color = "\033[93m"  # Yellow
    else:
        color = "\033[91m"  # Red
    reset = "\033[0m"
    return f"{color}{sharpe:.3f}{reset}"


def cmd_calculate(args):
    """Calculate Sharpe Ratio for a single crypto."""
    if len(args) < 1:
        print("Usage: calculate <coin_id> [days]")
        print("Example: calculate bitcoin 30")
        return

    coin_id = args[0]
    days = int(args[1]) if len(args) > 1 else 30

    calc = SharpeCalculator(get_db_config())
    result = calc.calculate_sharpe_ratio(coin_id, days)
    calc.close()

    if not result:
        print(f"\n❌ Insufficient data for {coin_id}")
        return

    print("\n" + "=" * 80)
    print(f"📊 Sharpe Ratio Analysis: {result['coin_id'].upper()}")
    print("=" * 80)

    print(f"\n📅 Analysis Period:")
    print(f"  Duration:            {result['period_days']:.1f} days")
    print(f"  From:                {result['first_date']}")
    print(f"  To:                  {result['last_date']}")

    print(f"\n💰 Performance:")
    print(f"  Starting Price:      {format_currency(result['first_price'])}")
    print(f"  Ending Price:        {format_currency(result['last_price'])}")
    print(f"  Total Return:        {format_percentage(result['percentage_return'])}")
    print(f"  Annualized Return:   {format_percentage(result['annualized_return'])}")

    print(f"\n📈 Risk Metrics:")
    print(f"  Volatility (annual): {result['annualized_volatility']:.2f}%")
    print(f"  Risk-Free Rate:      {result['risk_free_rate']:.2f}%")
    print(f"  Excess Return:       {format_percentage(result['excess_return'])}")

    print(f"\n🎯 Sharpe Ratio:")
    print(f"  Sharpe Ratio:        {format_sharpe(result['sharpe_ratio'])}")
    print(f"  Quality:             {result['sharpe_classification']}")

    print("\n💡 Interpretation:")
    if result['sharpe_ratio'] >= 2:
        print("  🚀 Excellent risk-adjusted returns!")
        print("  This crypto provides great returns relative to its risk.")
    elif result['sharpe_ratio'] >= 1:
        print("  ✅ Good risk-adjusted returns.")
        print("  Decent balance between risk and reward.")
    elif result['sharpe_ratio'] >= 0:
        print("  ⚠️  Acceptable but could be better.")
        print("  Returns barely justify the risk taken.")
    else:
        print("  ❌ Poor risk-adjusted returns.")
        print("  Returns don't compensate for the risk - consider alternatives.")

    print("=" * 80 + "\n")


def cmd_compare(args):
    """Compare Sharpe Ratios across all cryptos."""
    days = int(args[0]) if len(args) > 0 else 30

    calc = SharpeCalculator(get_db_config())
    coins = calc.get_available_coins()
    results = calc.compare_sharpe_ratios(coins, days)
    calc.close()

    if not results:
        print("❌ No results found")
        return

    print("\n" + "=" * 80)
    print(f"🏆 Sharpe Ratio Comparison (Last {days:.0f} days)")
    print("=" * 80)
    print("\nRanked by Risk-Adjusted Returns (Best to Worst)\n")

    for i, result in enumerate(results, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        print(f"{medal} {result['coin_id'].upper():12} | "
              f"Return: {format_percentage(result['annualized_return']):>10} | "
              f"Volatility: {result['annualized_volatility']:>6.2f}% | "
              f"Sharpe: {format_sharpe(result['sharpe_ratio']):>8} | "
              f"{result['sharpe_classification']}")

    print("\n" + "=" * 80)
    
    if len(results) > 0:
        best = results[0]
        worst = results[-1]
        print(f"\n🎯 Best Risk-Adjusted:  {best['coin_id'].upper()} "
              f"(Sharpe: {best['sharpe_ratio']:.3f})")
        print(f"⚠️  Worst Risk-Adjusted: {worst['coin_id'].upper()} "
              f"(Sharpe: {worst['sharpe_ratio']:.3f})\n")


def cmd_best(args):
    """Find the best risk-adjusted investment."""
    days = int(args[0]) if len(args) > 0 else 30

    calc = SharpeCalculator(get_db_config())
    coins = calc.get_available_coins()
    result = calc.find_best_risk_adjusted_investment(coins, days)
    calc.close()

    if not result:
        print("❌ No data available")
        return

    print("\n" + "=" * 80)
    print(f"🏆 Best Risk-Adjusted Investment (Last {days:.0f} days)")
    print("=" * 80)

    print(f"\n🎖️  Winner: {result['coin_id'].upper()}")
    print(f"   Ranked #{result['ranking']} out of {result['total_compared']} cryptos")

    print(f"\n📈 Performance:")
    print(f"  Annualized Return:   {format_percentage(result['annualized_return'])}")
    print(f"  Volatility:          {result['annualized_volatility']:.2f}%")
    print(f"  Sharpe Ratio:        {format_sharpe(result['sharpe_ratio'])}")
    print(f"  Quality:             {result['sharpe_classification']}")

    print(f"\n💡 Why it's the best:")
    print(f"  This crypto provides the highest return per unit of risk.")
    print(f"  It outperforms {result['better_than_pct']:.0f}% of the compared cryptos")
    print(f"  in terms of risk-adjusted returns.")

    print("=" * 80 + "\n")


def cmd_sortino(args):
    """Calculate Sortino Ratio (penalizes only downside volatility)."""
    if len(args) < 1:
        print("Usage: sortino <coin_id> [days]")
        print("Example: sortino ethereum 30")
        return

    coin_id = args[0]
    days = int(args[1]) if len(args) > 1 else 30

    calc = SharpeCalculator(get_db_config())
    result = calc.calculate_sortino_ratio(coin_id, days)
    calc.close()

    if not result:
        print(f"\n❌ Insufficient data for {coin_id}")
        return

    print("\n" + "=" * 80)
    print(f"📊 Sortino Ratio Analysis: {result['coin_id'].upper()}")
    print("=" * 80)

    print(f"\n📅 Period: {result['period_days']:.1f} days")

    print(f"\n💰 Performance:")
    print(f"  Total Return:        {format_percentage(result['percentage_return'])}")
    print(f"  Annualized Return:   {format_percentage(result['annualized_return'])}")

    print(f"\n📉 Risk Metrics:")
    print(f"  Downside Deviation:  {result['downside_deviation']:.2f}%")
    print(f"  Negative Days:       {result['negative_days']}/{result['total_days']}")
    print(f"  Win Rate:            {result['win_rate']:.1f}%")

    print(f"\n🎯 Sortino Ratio:")
    print(f"  Sortino Ratio:       {format_sharpe(result['sortino_ratio'])}")

    print("\n💡 Sortino vs Sharpe:")
    print("  Sortino only penalizes downside volatility (losses).")
    print("  Higher Sortino = Better at avoiding losses while still gaining.")
    print("  Good for risk-averse investors focused on capital preservation.")

    print("=" * 80 + "\n")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("\n📊 Sharpe Ratio Calculator CLI\n")
        print("Commands:")
        print("  calculate <coin> [days]          - Calculate Sharpe for one crypto")
        print("  compare [days]                   - Compare all cryptos by Sharpe")
        print("  best [days]                      - Find best risk-adjusted investment")
        print("  sortino <coin> [days]            - Calculate Sortino ratio")
        print("\nExamples:")
        print("  python test_sharpe.py calculate bitcoin 30")
        print("  python test_sharpe.py compare 7")
        print("  python test_sharpe.py best 30")
        print("  python test_sharpe.py sortino ethereum 30\n")
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "calculate": cmd_calculate,
        "compare": cmd_compare,
        "best": cmd_best,
        "sortino": cmd_sortino,
    }

    if command in commands:
        commands[command](args)
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: calculate, compare, best, sortino")


if __name__ == "__main__":
    main()
