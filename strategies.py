import pandas as pd
import numpy as np

class Strategy:
    def __init__(self, symbol, account_size=500):
        self.symbol = symbol
        self.account_size = account_size
        self.max_risk_per_trade = 0.01  # 1% of account
        self.max_daily_loss = 0.03  # 3% of account
        self.position = None

    def calculate_position_size(self, entry_price, stop_loss):
        risk_amount = self.account_size * self.max_risk_per_trade
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share > 0:
            return int(risk_amount / risk_per_share)
        return 0

    def evaluate(self, data):
        raise NotImplementedError


class SMAStrategy(Strategy):
    """Simple Moving Average Crossover Strategy"""
    def __init__(self, symbol, fast_period=50, slow_period=200, account_size=500):
        super().__init__(symbol, account_size)
        self.name = "SMA_Crossover"
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.stop_loss_pct = 0.02  # 2%

    def evaluate(self, data):
        if len(data) < self.slow_period:
            return None

        df = data.copy()
        df['SMA_Fast'] = df['close'].rolling(self.fast_period).mean()
        df['SMA_Slow'] = df['close'].rolling(self.slow_period).mean()

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # Entry signal: fast SMA crosses above slow SMA
        if (prev['SMA_Fast'] <= prev['SMA_Slow'] and
            latest['SMA_Fast'] > latest['SMA_Slow']):
            entry_price = latest['close']
            stop_loss = entry_price * (1 - self.stop_loss_pct)
            quantity = self.calculate_position_size(entry_price, stop_loss)
            return {
                'signal': 'BUY',
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'quantity': quantity,
                'reason': f'SMA({self.fast_period}) crossed above SMA({self.slow_period})'
            }

        # Exit signal: price closes below fast SMA
        if latest['close'] < latest['SMA_Fast'] and self.position:
            return {
                'signal': 'SELL',
                'exit_price': latest['close'],
                'reason': f'Price closed below SMA({self.fast_period})'
            }

        return None


class RSIStrategy(Strategy):
    """RSI Mean Reversion Strategy"""
    def __init__(self, symbol, period=14, oversold=30, overbought=70,
                 max_hold_days=10, account_size=500):
        super().__init__(symbol, account_size)
        self.name = "RSI_MeanReversion"
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self.max_hold_days = max_hold_days
        self.stop_loss_pct = 0.03  # 3%

    def calculate_rsi(self, data):
        df = data.copy()
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def evaluate(self, data):
        if len(data) < self.period + 1:
            return None

        rsi = self.calculate_rsi(data)
        latest_rsi = rsi.iloc[-1]
        latest_price = data['close'].iloc[-1]

        # Entry: RSI < 30 (oversold)
        if latest_rsi < self.oversold:
            stop_loss = latest_price * (1 - self.stop_loss_pct)
            quantity = self.calculate_position_size(latest_price, stop_loss)
            return {
                'signal': 'BUY',
                'entry_price': latest_price,
                'stop_loss': stop_loss,
                'quantity': quantity,
                'reason': f'RSI({self.period}) = {latest_rsi:.2f} (oversold)'
            }

        # Exit: RSI > 70 (overbought) or hold period exceeded
        if latest_rsi > self.overbought and self.position:
            return {
                'signal': 'SELL',
                'exit_price': latest_price,
                'reason': f'RSI({self.period}) = {latest_rsi:.2f} (overbought)'
            }

        return None


class BreakoutStrategy(Strategy):
    """Breakout Strategy"""
    def __init__(self, symbol, lookback_period=20, account_size=500):
        super().__init__(symbol, account_size)
        self.name = "Breakout"
        self.lookback_period = lookback_period
        self.stop_loss_pct = 0.025  # 2.5%

    def evaluate(self, data):
        if len(data) < self.lookback_period:
            return None

        df = data.copy()
        df['High_20'] = df['high'].rolling(self.lookback_period).max()
        df['Low_20'] = df['low'].rolling(self.lookback_period).min()

        latest = df.iloc[-1]
        prev = df.iloc[-2]
        latest_price = latest['close']

        # Entry: Price breaks above 20-day high
        if (prev['close'] <= prev['High_20'] and
            latest_price > latest['High_20']):
            stop_loss = latest_price * (1 - self.stop_loss_pct)
            quantity = self.calculate_position_size(latest_price, stop_loss)
            return {
                'signal': 'BUY',
                'entry_price': latest_price,
                'stop_loss': stop_loss,
                'quantity': quantity,
                'reason': f'Breakout above {self.lookback_period}-day high'
            }

        # Exit: Price closes below 20-day low
        if latest_price < latest['Low_20'] and self.position:
            return {
                'signal': 'SELL',
                'exit_price': latest_price,
                'reason': f'Closed below {self.lookback_period}-day low'
            }

        return None
