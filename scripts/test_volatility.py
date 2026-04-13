#!/usr/bin/env python3
"""
CLI to test the Volatility Calculator.
Usage examples:
  python test_volatility.py calculate bitcoin 30
  python test_volatility.py compare 7
  python test_volatility.py risk bitcoin 1000 30
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from pipelines.transform.volatility_calculator import VolatilityCalculator

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


def get_volatility_emoji(level):
    """Get emoji for volatility level."""
    if "Very Low" in level:
        return "🟢"
    elif "Low" in level:
        return "🟡"
    elif "Moderate" in level:
        return "🟠"
    elif "High" in level:
        return "🔴"
    else:
        return "⚫"


def cmd_calculate(args):
    """Calculate volatility for a single crypto."""
    if len(args) < 1:
        print("Usage: calculate <coin_id> [days]")
        print("Example: calculate bitcoin 30")
        return

    coin_id = args[0]
    days = int(args[1]) if len(args) > 1 else 30

    calc = VolatilityCalculator(get_db_config())
    result = calc.calculate_volatility(coin_id, days)
    calc.close()

    if not result:
        print(f"\n❌ No data available for {coin_id}")
        return

    print("\n" + "=" * 80)
    print(f"📊 Volatility Analysis: {result['coin_id'].upper()}")
    print("=" * 80)

    print(f"\n📅 Analysis Period:")
    print(f"  Duration:            {result['period_days']} days")
    print(f"  From:                {result['first_date']}")
    print(f"  To:                  {result['last_date']}")
    print(f"  Sample Size:         {result['sample_size']} data points")

    print(f"\n💰 Price Statistics:")
    print(f"  Average Price:       {format_currency(result['mean_price'])}")
    print(f"  Min Price:           {format_currency(result['min_price'])}")
    print(f"  Max Price:           {format_currency(result['max_price'])}")
    print(f"  Price Range:         {result['price_range_pct']:.2f}%")

    print(f"\n📈 Volatility Metrics:")
    print(f"  Standard Deviation:  {format_currency(result['std_dev'])}")
    print(f"  Variance:            {result['variance']:,.2f}")
    print(f"  Coefficient of Var:  {result['coefficient_of_variation']:.2f}%")

    emoji = get_volatility_emoji(result['volatility_level'])
    print(f"\n{emoji} Risk Level:          {result['volatility_level']}")
    print("=" * 80 + "\n")


def cmd_compare(args):
    """Compare volatility across all cryptos."""
    days = int(args[0]) if len(args) > 0 else 30

    calc = VolatilityCalculator(get_db_config())
    coins = calc.get_available_coins()
    results = calc.compare_volatility(coins, days)
    calc.close()

    if not results:
        print("❌ No results found")
        return

    print("\n" + "=" * 80)
    print(f"📊 Volatility Comparison (Last {days} days)")
    print("=" * 80)
    print("\nRanked by Risk (Least Risky → Most Risky)\n")

    for i, result in enumerate(results, 1):
        emoji = get_volatility_emoji(result['volatility_level'])
        medal = "🏆" if i == 1 else "⭐" if i == 2 else f"{i}."
        
        print(f"{medal} {emoji} {result['coin_id'].upper():12} | "
              f"Avg: {format_currency(result['mean_price']):>12} | "
              f"StdDev: {format_currency(result['std_dev']):>12} | "
              f"CV: {result['coefficient_of_variation']:>6.2f}% | "
              f"{result['volatility_level']}")

    print("\n" + "=" * 80)
    
    if len(results) > 0:
        safest = results[0]
        riskiest = results[-1]
        print(f"\n🛡️  Safest (Least Volatile):  {safest['coin_id'].upper()} "
              f"(CV: {safest['coefficient_of_variation']:.2f}%)")
        print(f"⚠️  Riskiest (Most Volatile): {riskiest['coin_id'].upper()} "
              f"(CV: {riskiest['coefficient_of_variation']:.2f}%)\n")


def cmd_risk(args):
    """Calculate risk-adjusted returns."""
    if len(args) < 2:
        print("Usage: risk <coin_id> <amount> [days]")
        print("Example: risk bitcoin 1000 30")
        return

    coin_id = args[0]
    amount = float(args[1])
    days = int(args[2]) if len(args) > 2 else 30

    calc = VolatilityCalculator(get_db_config())
    result = calc.get_risk_adjusted_returns(coin_id, amount, days)
    calc.close()

    if not result:
        print(f"\n❌ No data available for {coin_id}")
        return

    print("\n" + "=" * 80)
    print(f"⚖️  Risk-Adjusted Analysis: {result['coin_id'].upper()}")
    print("=" * 80)

    print(f"\n💰 Investment Scenario:")
    print(f"  Initial Investment:  {format_currency(result['investment_amount'])}")
    print(f"  Analysis Period:     {result['period_days']} days")

    if 'first_price' in result:
        print(f"\n📈 Performance:")
        print(f"  Starting Price:      {format_currency(result['first_price'])}")
        print(f"  Current Price:       {format_currency(result['last_price'])}")
        print(f"  Total Return:        {format_percentage(result['total_return_pct'])}")
        print(f"  Current Value:       {format_currency(result['current_value'])}")

    print(f"\n📊 Volatility:")
    print(f"  Standard Deviation:  {format_currency(result['std_dev'])}")
    print(f"  Coefficient of Var:  {result['coefficient_of_variation']:.2f}%")
    
    emoji = get_volatility_emoji(result['volatility_level'])
    print(f"  Risk Level:          {emoji} {result['volatility_level']}")

    if 'var_95_price' in result:
        print(f"\n⚠️  Value at Risk (95% confidence):")
        print(f"  VaR Price Level:     {format_currency(result['var_95_price'])}")
        print(f"  Potential Loss:      {format_percentage(result['potential_loss_pct'])}")
        print(f"  Amount at Risk:      {format_currency(abs(result['potential_loss_amount']))}")
        print(f"\n  💡 This means: In 95% of cases, your losses won't exceed "
              f"{format_currency(abs(result['potential_loss_amount']))}")

    print("=" * 80 + "\n")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("\n📊 Volatility Calculator CLI\n")
        print("Commands:")
        print("  calculate <coin> [days]          - Calculate volatility for one crypto")
        print("  compare [days]                   - Compare all cryptos by volatility")
        print("  risk <coin> <amount> [days]      - Risk-adjusted return analysis")
        print("\nExamples:")
        print("  python test_volatility.py calculate bitcoin 30")
        print("  python test_volatility.py compare 7")
        print("  python test_volatility.py risk ethereum 5000 30\n")
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "calculate": cmd_calculate,
        "compare": cmd_compare,
        "risk": cmd_risk,
    }

    if command in commands:
        commands[command](args)
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: calculate, compare, risk")


if __name__ == "__main__":
    main()
