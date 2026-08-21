#!/usr/bin/env python3
"""
Main entry point for the trading bot
Runs live trading on Alpaca paper trading account
"""

import os
import sys
from dotenv import load_dotenv
from live_trader import LiveTrader
import subprocess
import threading

load_dotenv()

def start_dashboard():
    """Start the Flask dashboard in a separate thread"""
    print("Starting dashboard on http://localhost:5000...")
    subprocess.Popen([sys.executable, "dashboard.py"])

def main():
    # Configuration
    symbol = os.getenv("SYMBOL", "SPY")
    api_key = os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("APCA_API_SECRET_KEY")

    # Validate credentials
    if not api_key or not secret_key:
        print("Error: Alpaca API credentials not found.")
        print("Please set APCA_API_KEY_ID and APCA_API_SECRET_KEY in .env file")
        print("You can copy .env.example to .env and fill in your credentials")
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"Trading Bot Started")
    print(f"Symbol: {symbol}")
    print(f"Mode: PAPER TRADING (No real money)")
    print(f"{'='*50}\n")

    # Start dashboard
    start_dashboard()

    # Start live trader
    trader = LiveTrader(symbol, api_key, secret_key)
    trader.start()

if __name__ == "__main__":
    main()
