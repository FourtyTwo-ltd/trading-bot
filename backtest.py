import pandas as pd
from datetime import datetime, timedelta
from strategies import SMAStrategy, RSIStrategy, BreakoutStrategy
from database import TradeDatabase

class Backtest:
    def __init__(self, symbol, start_date, end_date, initial_capital=500):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.trades = []
        self.signals = []
        self.db = TradeDatabase("backtest.db")

    def run_strategy(self, strategy, data):
        """Backtest a single strategy"""
        positions = []
        daily_pnl = 0

        for i in range(len(data)):
            current_data = data.iloc[:i+1].copy()
            signal = strategy.evaluate(current_data)

            if signal:
                if signal['signal'] == 'BUY' and not positions:
                    positions.append({
                        'entry_time': data.index[i],
                        'entry_price': signal['entry_price'],
                        'quantity': signal['quantity'],
                        'stop_loss': signal['stop_loss'],
                        'reason': signal['reason']
                    })
                    self.db.log_signal(strategy.name, self.symbol, 'BUY',
                                      signal['entry_price'], signal['reason'])

                elif signal['signal'] == 'SELL' and positions:
                    pos = positions.pop(0)
                    exit_price = signal['exit_price']
                    pnl = (exit_price - pos['entry_price']) * pos['quantity']
                    pnl_pct = ((exit_price - pos['entry_price']) / pos['entry_price']) * 100

                    self.trades.append({
                        'strategy': strategy.name,
                        'symbol': self.symbol,
                        'entry_time': pos['entry_time'],
                        'entry_price': pos['entry_price'],
                        'exit_time': data.index[i],
                        'exit_price': exit_price,
                        'quantity': pos['quantity'],
                        'pnl': pnl,
                        'pnl_pct': pnl_pct,
                        'reason': signal['reason']
                    })
                    daily_pnl += pnl
                    self.capital += pnl

                    self.db.log_trade(strategy.name, self.symbol,
                                     str(pos['entry_time']), pos['entry_price'],
                                     str(data.index[i]), exit_price,
                                     pos['quantity'], pnl, pnl_pct, signal['reason'])

            # Stop loss check
            if positions:
                current_price = data['close'].iloc[i]
                for pos in positions:
                    if current_price <= pos['stop_loss']:
                        pnl = (pos['stop_loss'] - pos['entry_price']) * pos['quantity']
                        pnl_pct = ((pos['stop_loss'] - pos['entry_price']) / pos['entry_price']) * 100

                        self.trades.append({
                            'strategy': strategy.name,
                            'symbol': self.symbol,
                            'entry_time': pos['entry_time'],
                            'entry_price': pos['entry_price'],
                            'exit_time': data.index[i],
                            'exit_price': pos['stop_loss'],
                            'quantity': pos['quantity'],
                            'pnl': pnl,
                            'pnl_pct': pnl_pct,
                            'reason': 'Stop loss hit'
                        })
                        daily_pnl += pnl
                        self.capital += pnl
                        positions.remove(pos)

        return {
            'strategy': strategy.name,
            'trades': self.trades,
            'capital': self.capital,
            'return_pct': ((self.capital - self.initial_capital) / self.initial_capital) * 100
        }

    def generate_report(self):
        """Generate backtest report"""
        if not self.trades:
            return "No trades executed"

        df = pd.DataFrame(self.trades)
        total_trades = len(df)
        winning_trades = len(df[df['pnl'] > 0])
        losing_trades = len(df[df['pnl'] <= 0])
        total_pnl = df['pnl'].sum()
        avg_return = df['pnl_pct'].mean()
        max_return = df['pnl_pct'].max()
        min_return = df['pnl_pct'].min()
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        report = f"""
========== BACKTEST REPORT ==========
Total Trades: {total_trades}
Winning Trades: {winning_trades}
Losing Trades: {losing_trades}
Win Rate: {win_rate:.2f}%
Total P&L: ${total_pnl:.2f}
Average Return per Trade: {avg_return:.2f}%
Max Return: {max_return:.2f}%
Min Return: {min_return:.2f}%
Final Capital: ${self.capital:.2f}
Total Return: {((self.capital - self.initial_capital) / self.initial_capital) * 100:.2f}%
====================================
"""
        return report
