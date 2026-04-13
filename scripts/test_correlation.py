#!/usr/bin/env python3
"""
CLI to test the Correlation Calculator.
Usage examples:
  python test_correlation.py pair bitcoin ethereum 30
  python test_correlation.py matrix 7
  python test_correlation.py best 30
  python test_correlation.py worst 30
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from pipelines.transform.correlation_calculator import CorrelationCalculator

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


def format_correlation(corr):
    """Format correlation with color."""
    if corr >= 0.7:
        color = "\033[91m"  # Red - high correlation, poor diversification
    elif corr >= 0.4:
        color = "\033[93m"  # Yellow - moderate
    else:
        color = "\033[92m"  # Green - low correlation, good diversification
    reset = "\033[0m"
    return f"{color}{corr:+.3f}{reset}"


def cmd_pair(args):
    """Calculate correlation between two cryptos."""
    if len(args) < 2:
        print("Usage: pair <coin1> <coin2> [days]")
        print("Example: pair bitcoin ethereum 30")
        return

    coin1 = args[0]
    coin2 = args[1]
    days = int(args[2]) if len(args) > 2 else 30

    calc = CorrelationCalculator(get_db_config())
    result = calc.calculate_correlation(coin1, coin2, days)
    calc.close()

    if not result:
        print(f"\n❌ Insufficient data for {coin1} and {coin2}")
        return

    print("\n" + "=" * 80)
    print(f"🔗 Correlation Analysis: {result['coin1'].upper()} ↔ {result['coin2'].upper()}")
    print("=" * 80)

    print(f"\n📊 Analysis Details:")
    print(f"  Period:              {result['period_days']} days")
    print(f"  Sample Size:         {result['sample_size']} matching data points")

    print(f"\n📈 Correlation Metrics:")
    print(f"  Correlation:         {format_correlation(result['correlation'])}")
    print(f"  Strength:            {result['strength']}")

    print(f"\n💼 Portfolio Impact:")
    print(f"  {result['diversification_benefit']}")

    print("\n💡 Interpretation:")
    if result['correlation'] >= 0.7:
        print("  These cryptos move together strongly.")
        print("  Investing in both provides LIMITED diversification.")
    elif result['correlation'] >= 0.4:
        print("  These cryptos have moderate correlation.")
        print("  Investing in both provides SOME diversification benefit.")
    elif result['correlation'] >= 0:
        print("  These cryptos have low correlation.")
        print("  Investing in both provides GOOD diversification!")
    else:
        print("  These cryptos move in opposite directions!")
        print("  Investing in both provides EXCELLENT diversification (hedge)!")

    print("=" * 80 + "\n")


def cmd_matrix(args):
    """Display full correlation matrix."""
    days = int(args[0]) if len(args) > 0 else 30

    calc = CorrelationCalculator(get_db_config())
    coins = calc.get_available_coins()
    result = calc.calculate_correlation_matrix(coins, days)
    calc.close()

    print("\n" + "=" * 80)
    print(f"🔗 Correlation Matrix (Last {days} days)")
    print("=" * 80)

    # Print header
    print(f"\n{'':12} ", end="")
    for coin in result['coin_ids']:
        print(f"{coin[:8]:>10}", end="")
    print()
    print("-" * (12 + 10 * len(result['coin_ids'])))

    # Print matrix rows
    for coin1 in result['coin_ids']:
        print(f"{coin1:12} ", end="")
        for coin2 in result['coin_ids']:
            corr = result['matrix'][coin1][coin2]
            if corr is not None:
                if coin1 == coin2:
                    print(f"{'1.000':>10}", end="")
                else:
                    print(f"{corr:>10.3f}", end="")
            else:
                print(f"{'N/A':>10}", end="")
        print()

    print("\n" + "=" * 80)
    print(f"\n📊 Portfolio Diversification Score:")
    score_info = result['diversification_score']
    print(f"  Score:               {score_info['score']:.1f}/100")
    print(f"  Rating:              {score_info['rating']}")
    print(f"  Average Correlation: {result['average_correlation']:+.3f}")
    
    print(f"\n💡 {score_info['interpretation']}")
    print("=" * 80 + "\n")


def cmd_best(args):
    """Find best diversification pairs."""
    days = int(args[0]) if len(args) > 0 else 30

    calc = CorrelationCalculator(get_db_config())
    coins = calc.get_available_coins()
    pairs = calc.find_best_diversification_pairs(coins, days)
    calc.close()

    if not pairs:
        print("❌ No correlation data available")
        return

    print("\n" + "=" * 80)
    print(f"🌟 Best Diversification Pairs (Last {days} days)")
    print("=" * 80)
    print("\nThese crypto pairs provide the BEST diversification for your portfolio:\n")

    for i, pair in enumerate(pairs, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        print(f"{medal} {pair['coin1'].upper():12} ↔ {pair['coin2'].upper():12}")
        print(f"   Correlation:      {format_correlation(pair['correlation'])}")
        print(f"   Strength:         {pair['strength']}")
        print(f"   Diversification:  {pair['diversification_benefit']}")
        print()

    print("💡 Tip: Build your portfolio with these pairs for maximum diversification!")
    print("=" * 80 + "\n")


def cmd_worst(args):
    """Find worst diversification pairs (highest correlation)."""
    days = int(args[0]) if len(args) > 0 else 30

    calc = CorrelationCalculator(get_db_config())
    coins = calc.get_available_coins()
    pairs = calc.find_worst_diversification_pairs(coins, days)
    calc.close()

    if not pairs:
        print("❌ No correlation data available")
        return

    print("\n" + "=" * 80)
    print(f"⚠️  Worst Diversification Pairs (Last {days} days)")
    print("=" * 80)
    print("\nThese crypto pairs move together - avoid combining them:\n")

    for i, pair in enumerate(pairs, 1):
        print(f"{i}. {pair['coin1'].upper():12} ↔ {pair['coin2'].upper():12}")
        print(f"   Correlation:      {format_correlation(pair['correlation'])}")
        print(f"   Strength:         {pair['strength']}")
        print(f"   Diversification:  {pair['diversification_benefit']}")
        print()

    print("⚠️  Warning: Investing in these pairs provides limited diversification!")
    print("=" * 80 + "\n")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("\n🔗 Correlation Calculator CLI\n")
        print("Commands:")
        print("  pair <coin1> <coin2> [days]     - Correlation between two cryptos")
        print("  matrix [days]                   - Full correlation matrix")
        print("  best [days]                     - Best diversification pairs")
        print("  worst [days]                    - Worst diversification pairs")
        print("\nExamples:")
        print("  python test_correlation.py pair bitcoin ethereum 30")
        print("  python test_correlation.py matrix 7")
        print("  python test_correlation.py best 30")
        print("  python test_correlation.py worst 30\n")
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "pair": cmd_pair,
        "matrix": cmd_matrix,
        "best": cmd_best,
        "worst": cmd_worst,
    }

    if command in commands:
        commands[command](args)
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: pair, matrix, best, worst")


if __name__ == "__main__":
    main()
