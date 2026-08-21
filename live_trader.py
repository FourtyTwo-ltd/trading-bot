import time
import pandas as pd
from datetime import datetime
import schedule
from alpaca_connector import AlpacaConnector
from strategies import SMAStrategy, RSIStrategy, BreakoutStrategy
from database import TradeDatabase

class LiveTrader:
    def __init__(self, symbol, api_key=None, secret_key=None):
        self.symbol = symbol
        self.alpaca = AlpacaConnector(api_key, secret_key)
        self.db = TradeDatabase("trades.db")
        self.strategies = [
            SMAStrategy(symbol),
            RSIStrategy(symbol),
            BreakoutStrategy(symbol)
        ]
        self.positions = {}  # Track open positions
        self.daily_pnl = 0
        self.max_daily_loss = 15  # 3% of $500

    def fetch_latest_data(self, lookback_days=200):
        """Fetch latest market data"""
        data = self.alpaca.get_historical_data(self.symbol, days=lookback_days, timeframe="1Day")
        return data

    def evaluate_strategies(self, data):
        """Evaluate all strategies against current data"""
        signals = []

        for strategy in self.strategies:
            try:
                signal = strategy.evaluate(data)
                if signal:
                    self.db.log_signal(strategy.name, self.symbol,
                                      signal['signal'], signal.get('entry_price', signal.get('exit_price')),
                                      signal['reason'])
                    signals.append((strategy.name, signal))
                    print(f"[{strategy.name}] {signal['signal']}: {signal['reason']}")
            except Exception as e:
                print(f"Error evaluating {strategy.name}: {e}")

        return signals

    def execute_buy_signal(self, strategy_name, signal):
        """Execute a buy order"""
        try:
            quantity = signal['quantity']
            entry_price = signal['entry_price']
            stop_loss = signal['stop_loss']

            # Check daily loss limit
            if self.daily_pnl <= -self.max_daily_loss:
                print(f"Daily loss limit reached. Skipping buy order.")
                return

            # Place order
            order = self.alpaca.place_order(self.symbol, quantity, 'buy')
            if order:
                self.positions[strategy_name] = {
                    'entry_time': datetime.now(),
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'quantity': quantity,
                    'order_id': order['order_id']
                }
                print(f"Buy order placed: {quantity} shares at ~${entry_price:.2f}")
                return True

        except Exception as e:
            print(f"Error executing buy signal: {e}")

        return False

    def execute_sell_signal(self, strategy_name, signal):
        """Execute a sell order"""
        try:
            if strategy_name not in self.positions:
                return False

            pos = self.positions[strategy_name]
            quantity = pos['quantity']

            order = self.alpaca.place_order(self.symbol, quantity, 'sell')
            if order:
                exit_price = signal['exit_price']
                pnl = (exit_price - pos['entry_price']) * quantity
                pnl_pct = ((exit_price - pos['entry_price']) / pos['entry_price']) * 100

                self.daily_pnl += pnl

                self.db.log_trade(strategy_name, self.symbol,
                                 str(pos['entry_time']), pos['entry_price'],
                                 str(datetime.now()), exit_price,
                                 quantity, pnl, pnl_pct, signal['reason'])

                del self.positions[strategy_name]
                print(f"Sell order placed: {quantity} shares at ~${exit_price:.2f} | P&L: ${pnl:.2f} ({pnl_pct:.2f}%)")
                return True

        except Exception as e:
            print(f"Error executing sell signal: {e}")

        return False

    def check_stop_losses(self, current_price):
        """Check if any positions hit stop loss"""
        for strategy_name, pos in list(self.positions.items()):
            if current_price <= pos['stop_loss']:
                print(f"Stop loss triggered for {strategy_name} at ${current_price:.2f}")
                pnl = (pos['stop_loss'] - pos['entry_price']) * pos['quantity']
                self.daily_pnl += pnl
                self.alpaca.place_order(self.symbol, pos['quantity'], 'sell')
                del self.positions[strategy_name]

    def print_account_status(self):
        """Print current account status"""
        account = self.alpaca.get_account_info()
        if account:
            print(f"\n=== ACCOUNT STATUS ===")
            print(f"Cash: ${account['cash']:.2f}")
            print(f"Equity: ${account['equity']:.2f}")
            print(f"Buying Power: ${account['buying_power']:.2f}")
            print(f"Daily P&L: ${self.daily_pnl:.2f}")
            print(f"Open Positions: {len(self.positions)}")
            stats = self.db.get_stats()
            print(f"Total Trades: {stats['total_trades']}")
            print(f"Win Rate: {(stats['winning_trades'] / stats['total_trades'] * 100) if stats['total_trades'] > 0 else 0:.2f}%")

    def run_once(self):
        """Execute one evaluation cycle"""
        try:
            print(f"\n[{datetime.now()}] Evaluating strategies...")
            data = self.fetch_latest_data()

            if data is None or len(data) == 0:
                print("No data available")
                return

            signals = self.evaluate_strategies(data)

            for strategy_name, signal in signals:
                if signal['signal'] == 'BUY':
                    self.execute_buy_signal(strategy_name, signal)
                elif signal['signal'] == 'SELL':
                    self.execute_sell_signal(strategy_name, signal)

            current_price = data['close'].iloc[-1]
            self.check_stop_losses(current_price)

            self.print_account_status()

        except Exception as e:
            print(f"Error in run_once: {e}")

    def start(self):
        """Start the live trading bot"""
        print(f"Starting live trader for {self.symbol}...")
        self.print_account_status()

        # Schedule to run every hour during market hours
        schedule.every().hour.at(":00").do(self.run_once)

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\nShutting down trader...")
