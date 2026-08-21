import os
from alpaca_trade_api import REST
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class AlpacaConnector:
    def __init__(self, api_key=None, secret_key=None):
        self.api_key = api_key or os.getenv("APCA_API_KEY_ID")
        self.secret_key = secret_key or os.getenv("APCA_API_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials not found. Set APCA_API_KEY_ID and APCA_API_SECRET_KEY")

        self.api = REST(key_id=self.api_key, secret_key=self.secret_key, base_url='https://paper-api.alpaca.markets')

    def get_historical_data(self, symbol, days=365):
        """Fetch historical OHLCV data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            bars = self.api.get_barset(symbol, 'day', limit=days)
            if symbol not in bars:
                return None

            df_data = []
            for bar in bars[symbol]:
                df_data.append({
                    'date': pd.to_datetime(bar.t),
                    'open': bar.o,
                    'high': bar.h,
                    'low': bar.l,
                    'close': bar.c,
                    'volume': bar.v
                })

            df = pd.DataFrame(df_data)
            df.set_index('date', inplace=True)
            return df

        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

    def get_account_info(self):
        """Get account information"""
        try:
            account = self.api.get_account()
            return {
                'cash': float(account.cash),
                'equity': float(account.equity),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value)
            }
        except Exception as e:
            print(f"Error fetching account info: {e}")
            return None

    def place_order(self, symbol, quantity, side='buy'):
        """Place a market order"""
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=quantity,
                side=side,
                type='market',
                time_in_force='day'
            )
            return {
                'order_id': order.id,
                'symbol': order.symbol,
                'quantity': order.qty,
                'side': order.side,
                'status': order.status
            }
        except Exception as e:
            print(f"Error placing order: {e}")
            return None

    def get_open_positions(self):
        """Get all open positions"""
        try:
            positions = self.api.list_positions()
            return positions
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []

    def close_position(self, symbol):
        """Close a position"""
        try:
            self.api.close_position(symbol)
            return True
        except Exception as e:
            print(f"Error closing position: {e}")
            return False
