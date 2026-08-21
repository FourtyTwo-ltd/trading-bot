#!/usr/bin/env python3
"""
Backtest all strategies on historical data
This is the first step - test strategies before live trading
"""

import pandas as pd
from datetime import datetime, timedelta
from alpaca_connector import AlpacaConnector
from backtest import Backtest
from strategies import SMAStrategy, RSIStrategy, BreakoutStrategy
import os

def run_backtest():
    symbol = "SPY"
    initial_capital = 500
    lookback_days = 365

    print(f"\n{'='*50}")
    print(f"Starting Backtest: {symbol}")
    print(f"Initial Capital: ${initial_capital}")
    print(f"Lookback Period: {lookback_days} days")
    print(f"{'='*50}\n")

    # Fetch historical data
    try:
        connector = AlpacaConnector()
        data = connector.get_historical_data(symbol, days=lookback_days)

        if data is None or len(data) == 0:
            print("Error: Could not fetch data. Make sure API credentials are set.")
            return

        print(f"Data fetched: {len(data)} bars from {data.index[0]} to {data.index[-1]}\n")

    except Exception as e:
        print(f"Error fetching data: {e}")
        print("Make sure you have set APCA_API_KEY_ID and APCA_API_SECRET_KEY in .env")
        return

    # Initialize backtest
    bt = Backtest(symbol, data.index[0], data.index[-1], initial_capital)

    # Test each strategy
    strategies = [
        SMAStrategy(symbol),
        RSIStrategy(symbol),
        BreakoutStrategy(symbol)
    ]

    results = {}
    for strategy in strategies:
        print(f"\nTesting {strategy.name}...")
        result = bt.run_strategy(strategy, data)
        results[strategy.name] = result

    # Print reports
    for strategy_name, result in results.items():
        bt.trades = result['trades']
        bt.capital = result['capital']
        print(f"\n{'='*50}")
        print(f"{strategy_name.upper()} BACKTEST RESULTS")
        print(f"{'='*50}")
        print(bt.generate_report())

    # Summary comparison
    print(f"\n{'='*50}")
    print(f"STRATEGY COMPARISON")
    print(f"{'='*50}")
    print(f"{'Strategy':<20} {'Trades':<10} {'Win Rate':<15} {'Total P&L':<15}")
    print(f"{'-'*60}")

    for strategy_name, result in results.items():
        if result['trades']:
            df = pd.DataFrame(result['trades'])
            total_trades = len(df)
            wins = len(df[df['pnl'] > 0])
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            total_pnl = df['pnl'].sum()
            print(f"{strategy_name:<20} {total_trades:<10} {win_rate:>6.2f}%{'':<8} ${total_pnl:>10.2f}")

    print(f"\nBacktest complete! Check 'backtest.db' for detailed trade logs.")

if __name__ == "__main__":
    run_backtest()
