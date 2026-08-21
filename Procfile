web: python dashboard.py
trader: python -c "from live_trader import LiveTrader; import os; from dotenv import load_dotenv; load_dotenv(); trader = LiveTrader(os.getenv('SYMBOL', 'SPY'), os.getenv('APCA_API_KEY_ID'), os.getenv('APCA_API_SECRET_KEY')); trader.start()"
