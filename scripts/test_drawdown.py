#!/usr/bin/env python3
"""
CLI to test the Drawdown Calculator.
Usage examples:
  python test_drawdown.py calculate bitcoin 30
  python test_drawdown.py compare 7
  python test_drawdown.py worst bitcoin 30
  python test_drawdown.py underwater ethereum 30
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from pipelines.transform.drawdown_calculator import DrawdownCalculator

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


def cmd_calculate(args):
    """Calculate maximum drawdown for a single crypto."""
    if len(args) < 1:
        print("Usage: calculate <coin_id> [days]")
        print("Example: calculate bitcoin 30")
        return

    coin_id = args[0]
    days = int(args[1]) if len(args) > 1 else 30

    calc = DrawdownCalculator(get_db_config())
    result = calc.calculate_drawdown(coin_id, days)
    calc.close()

    if not result:
        print(f"\n❌ Insufficient data for {coin_id}")
        return

    print("\n" + "=" * 80)
    print(f"📉 Maximum Drawdown Analysis: {result['coin_id'].upper()}")
    print("=" * 80)

    print(f"\n📅 Analysis Period:")
    print(f"  Duration:            {result['period_days']:.0f} days")
    print(f"  From:                {result['first_date']}")
    print(f"  To:                  {result['last_date']}")
    print(f"  Sample Size:         {result['sample_size']} data points")

    print(f"\n💰 Price Extremes:")
    print(f"  Period High:         {format_currency(result['period_high'])}")
    print(f"  High Date:           {result['period_high_date']}")
    print(f"  Current Price:       {format_currency(result['current_price'])}")

    if result['max_drawdown_info']:
        dd_info = result['max_drawdown_info']
        print(f"\n📉 Maximum Drawdown Event:")
        print(f"  Peak Price:          {format_currency(dd_info['peak_price'])}")
        print(f"  Peak Date:           {dd_info['peak_timestamp']}")
        print(f"  Trough Price:        {format_currency(dd_info['trough_price'])}")
        print(f"  Trough Date:         {dd_info['trough_timestamp']}")
        print(f"  Max Drawdown:        {format_percentage(dd_info['drawdown_pct'])}")
        
        # Calculate decline duration
        decline = dd_info['trough_timestamp'] - dd_info['peak_timestamp']
        decline_hours = decline.total_seconds() / 3600
        print(f"  Decline Duration:    {decline_hours:.1f} hours ({decline_hours/24:.1f} days)")

    print(f"\n📊 Current Status:")
    print(f"  Current Drawdown:    {format_percentage(result['current_drawdown_pct'])}")
    status = "✅ Yes - At new high!" if result['is_at_new_high'] else "⚠️  No - Still below peak"
    print(f"  At New High:         {status}")

    if result['recovery_time_days']:
        print(f"  Recovery Time:       {result['recovery_time_days']:.1f} days")

    print(f"\n⚠️  Risk Assessment:")
    print(f"  {result['risk_classification']}")

    print("\n💡 What this means:")
    abs_dd = abs(result['max_drawdown_pct'])
    if abs_dd < 5:
        print("  Very stable crypto - minimal downside risk observed.")
    elif abs_dd < 10:
        print("  Low risk - manageable drawdowns for most investors.")
    elif abs_dd < 20:
        print("  Moderate risk - expect occasional significant drops.")
    elif abs_dd < 30:
        print("  High risk - be prepared for large drawdowns.")
    else:
        print("  Extreme risk - only for risk-tolerant investors!")
    
    print(f"  In the worst case, you could have lost {abs_dd:.1f}% from the peak.")

    print("=" * 80 + "\n")


def cmd_compare(args):
    """Compare drawdowns across all cryptos."""
    days = int(args[0]) if len(args) > 0 else 30

    calc = DrawdownCalculator(get_db_config())
    coins = calc.get_available_coins()
    results = calc.compare_drawdowns(coins, days)
    calc.close()

    if not results:
        print("❌ No results found")
        return

    print("\n" + "=" * 80)
    print(f"📉 Maximum Drawdown Comparison (Last {days:.0f} days)")
    print("=" * 80)
    print("\nRanked by Risk (Safest → Riskiest)\n")

    for i, result in enumerate(results, 1):
        medal = "🛡️" if i == 1 else "⭐" if i == 2 else f"{i}."
        abs_dd = abs(result['max_drawdown_pct'])
        
        status = "✅" if result['is_at_new_high'] else "⚠️ "
        
        print(f"{medal} {result['coin_id'].upper():12} | "
              f"Max DD: {format_percentage(result['max_drawdown_pct']):>10} | "
              f"Current DD: {format_percentage(result['current_drawdown_pct']):>10} | "
              f"{status} {result['risk_classification']}")

    print("\n" + "=" * 80)
    
    if len(results) > 0:
        safest = results[0]
        riskiest = results[-1]
        print(f"\n🛡️  Safest (Smallest Drawdown):  {safest['coin_id'].upper()} "
              f"({abs(safest['max_drawdown_pct']):.2f}% max drop)")
        print(f"⚠️  Riskiest (Largest Drawdown): {riskiest['coin_id'].upper()} "
              f"({abs(riskiest['max_drawdown_pct']):.2f}% max drop)\n")


def cmd_worst(args):
    """Find worst possible investment timing."""
    if len(args) < 1:
        print("Usage: worst <coin_id> [days]")
        print("Example: worst bitcoin 30")
        return

    coin_id = args[0]
    days = int(args[1]) if len(args) > 1 else 30

    calc = DrawdownCalculator(get_db_config())
    result = calc.get_worst_investment_timing(coin_id, days)
    calc.close()

    if not result:
        print(f"\n❌ Insufficient data for {coin_id}")
        return

    print("\n" + "=" * 80)
    print(f"😱 Worst Investment Timing: {result['coin_id'].upper()}")
    print("=" * 80)

    print(f"\n💸 Nightmare Scenario:")
    print(f"  You bought at:       {result['worst_buy_date']}")
    print(f"  Buy Price:           {format_currency(result['worst_buy_price'])}")
    print(f"  Investment:          {format_currency(result['investment_amount'])}")
    print(f"  Quantity:            {result['quantity']:.8f} {result['coin_id'].upper()}")

    print(f"\n📉 At the Worst Point (Trough):")
    print(f"  Trough Date:         {result['trough_date']}")
    print(f"  Trough Price:        {format_currency(result['trough_price'])}")
    print(f"  Portfolio Value:     {format_currency(result['value_at_trough'])}")
    print(f"  Loss:                {format_currency(result['loss_at_trough'])}")
    print(f"  Loss %:              {format_percentage(result['loss_pct_at_trough'])}")

    print(f"\n📊 Current Status:")
    print(f"  Current Price:       {format_currency(result['current_price'])}")
    print(f"  Current Value:       {format_currency(result['current_value'])}")
    
    pnl_color = "\033[92m" if result['current_pnl'] >= 0 else "\033[91m"
    reset = "\033[0m"
    print(f"  P&L:                 {pnl_color}{format_currency(result['current_pnl'])}{reset}")
    print(f"  ROI:                 {format_percentage(result['current_pnl_pct'])}")
    
    recovery_status = "✅ YES" if result['has_recovered'] else "❌ NO"
    print(f"  Recovered:           {recovery_status}")

    print("\n💡 Lesson:")
    if result['has_recovered']:
        print("  Even the worst timing eventually recovered!")
        print("  Patience and holding through drawdowns can pay off.")
    else:
        print("  Still underwater from the worst entry point.")
        print("  This shows the importance of buying during dips, not peaks!")

    print("=" * 80 + "\n")


def cmd_underwater(args):
    """Calculate underwater periods."""
    if len(args) < 1:
        print("Usage: underwater <coin_id> [days]")
        print("Example: underwater ethereum 30")
        return

    coin_id = args[0]
    days = int(args[1]) if len(args) > 1 else 30

    calc = DrawdownCalculator(get_db_config())
    result = calc.calculate_underwater_periods(coin_id, days)
    calc.close()

    if not result:
        print(f"\n❌ Insufficient data for {coin_id}")
        return

    print("\n" + "=" * 80)
    print(f"🌊 Underwater Analysis: {result['coin_id'].upper()}")
    print("=" * 80)

    print(f"\n📊 Time Spent Below Peak:")
    print(f"  Total Periods:       {result['total_periods']}")
    print(f"  Underwater Periods:  {result['underwater_periods']}")
    print(f"  Underwater %:        {result['underwater_pct']:.1f}%")
    print(f"  Above Water %:       {result['above_water_pct']:.1f}%")

    print("\n💡 Interpretation:")
    if result['underwater_pct'] < 20:
        print("  🌟 Excellent! Rarely underwater - strong upward trend.")
    elif result['underwater_pct'] < 50:
        print("  ✅ Good! Spends most time near or at peaks.")
    elif result['underwater_pct'] < 80:
        print("  ⚠️  Caution! Often below previous highs - volatile.")
    else:
        print("  ❌ Warning! Almost always underwater - struggling asset.")

    print("=" * 80 + "\n")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("\n📉 Drawdown Calculator CLI\n")
        print("Commands:")
        print("  calculate <coin> [days]          - Calculate max drawdown")
        print("  compare [days]                   - Compare all cryptos by drawdown")
        print("  worst <coin> [days]              - Worst investment timing scenario")
        print("  underwater <coin> [days]         - Time spent below peak")
        print("\nExamples:")
        print("  python test_drawdown.py calculate bitcoin 30")
        print("  python test_drawdown.py compare 7")
        print("  python test_drawdown.py worst ethereum 30")
        print("  python test_drawdown.py underwater solana 30\n")
        return

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "calculate": cmd_calculate,
        "compare": cmd_compare,
        "worst": cmd_worst,
        "underwater": cmd_underwater,
    }

    if command in commands:
        commands[command](args)
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: calculate, compare, worst, underwater")


if __name__ == "__main__":
    main()
