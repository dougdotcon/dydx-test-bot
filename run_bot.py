"""
Script to run the dYdX trading bot with specific parameters.
"""
import subprocess
import sys
import time
import argparse

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Run dYdX Trading Bot")
    
    parser.add_argument("--market", default="ETH-USD", help="Market symbol (e.g., 'ETH-USD')")
    parser.add_argument("--timeframe", default="1MIN", help="Candle timeframe (e.g., '1MIN', '5MINS')")
    parser.add_argument("--volume-factor", type=float, default=2.0, help="Volume factor for breakout confirmation")
    parser.add_argument("--resistance-periods", type=int, default=24, help="Number of periods to look back for resistance")
    parser.add_argument("--risk-reward", type=float, default=3.0, help="Risk-to-reward ratio for take profit calculation")
    parser.add_argument("--position-size", type=float, default=100.0, help="Position size in USD")
    parser.add_argument("--update-interval", type=int, default=60, help="Interval in seconds between market data updates")
    parser.add_argument("--duration", type=int, default=3600, help="Duration to run the bot in seconds (0 for indefinite)")
    
    return parser.parse_args()

def main():
    """
    Run the dYdX trading bot with the specified parameters.
    """
    args = parse_args()
    
    # Build command
    cmd = [
        "python", "bot.py",
        "--market", args.market,
        "--timeframe", args.timeframe,
        "--volume-factor", str(args.volume_factor),
        "--resistance-periods", str(args.resistance_periods),
        "--risk-reward", str(args.risk_reward),
        "--position-size", str(args.position_size),
        "--update-interval", str(args.update_interval)
    ]
    
    print(f"Starting dYdX Trading Bot with the following parameters:")
    print(f"  Market: {args.market}")
    print(f"  Timeframe: {args.timeframe}")
    print(f"  Volume Factor: {args.volume_factor}")
    print(f"  Resistance Periods: {args.resistance_periods}")
    print(f"  Risk:Reward Ratio: {args.risk_reward}")
    print(f"  Position Size: ${args.position_size}")
    print(f"  Update Interval: {args.update_interval}s")
    
    if args.duration > 0:
        print(f"  Duration: {args.duration}s")
    else:
        print("  Duration: Indefinite (press Ctrl+C to stop)")
    
    # Start the bot
    process = subprocess.Popen(cmd)
    
    try:
        # Wait for the specified duration or indefinitely
        if args.duration > 0:
            print(f"Bot will run for {args.duration} seconds...")
            time.sleep(args.duration)
            print("Time's up! Stopping the bot...")
            process.terminate()
        else:
            # Wait indefinitely
            process.wait()
    
    except KeyboardInterrupt:
        print("Stopping the bot...")
        process.terminate()
    
    # Wait for the process to terminate
    process.wait()
    print("Bot stopped.")

if __name__ == "__main__":
    main()
