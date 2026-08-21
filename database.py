import sqlite3
from datetime import datetime
import json

class TradeDatabase:
    def __init__(self, db_path="trades.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS signals
                     (id INTEGER PRIMARY KEY, timestamp TEXT, strategy TEXT,
                      symbol TEXT, signal_type TEXT, price REAL, reason TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS trades
                     (id INTEGER PRIMARY KEY, timestamp TEXT, strategy TEXT,
                      symbol TEXT, entry_time TEXT, entry_price REAL,
                      exit_time TEXT, exit_price REAL, quantity INTEGER,
                      pnl REAL, pnl_pct REAL, reason TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS daily_stats
                     (id INTEGER PRIMARY KEY, date TEXT, total_trades INTEGER,
                      winning_trades INTEGER, losing_trades INTEGER,
                      daily_pnl REAL, max_drawdown REAL)''')

        conn.commit()
        conn.close()

    def log_signal(self, strategy, symbol, signal_type, price, reason):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        c.execute('''INSERT INTO signals
                     (timestamp, strategy, symbol, signal_type, price, reason)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (timestamp, strategy, symbol, signal_type, price, reason))
        conn.commit()
        conn.close()

    def log_trade(self, strategy, symbol, entry_time, entry_price, exit_time,
                  exit_price, quantity, pnl, pnl_pct, reason):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO trades
                     (timestamp, strategy, symbol, entry_time, entry_price,
                      exit_time, exit_price, quantity, pnl, pnl_pct, reason)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (datetime.now().isoformat(), strategy, symbol, entry_time,
                   entry_price, exit_time, exit_price, quantity, pnl, pnl_pct, reason))
        conn.commit()
        conn.close()

    def get_daily_pnl(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT SUM(pnl) FROM trades
                     WHERE DATE(timestamp) = DATE('now')''')
        result = c.fetchone()[0]
        conn.close()
        return result or 0

    def get_all_trades(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM trades')
        trades = c.fetchall()
        conn.close()
        return trades

    def get_stats(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT COUNT(*), SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END),
                            SUM(pnl), AVG(pnl_pct) FROM trades''')
        total, wins, total_pnl, avg_return = c.fetchone()
        conn.close()
        return {
            'total_trades': total or 0,
            'winning_trades': wins or 0,
            'total_pnl': total_pnl or 0,
            'avg_return_pct': avg_return or 0
        }
