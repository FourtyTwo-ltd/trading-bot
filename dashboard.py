from flask import Flask, jsonify, render_template_string
from database import TradeDatabase
import pandas as pd
import os
import threading
from dotenv import load_dotenv
from alpaca_connector import AlpacaConnector
from strategies import SMAStrategy, RSIStrategy, BreakoutStrategy
from datetime import datetime, time
import pytz
import json

load_dotenv()

app = Flask(__name__)
db = TradeDatabase("trades.db")

def is_market_open():
    """Check if US stock market is currently open"""
    et = pytz.timezone('US/Eastern')
    now = datetime.now(et)

    if now.weekday() >= 5:
        return False

    market_open = time(9, 30)
    market_close = time(16, 0)

    return market_open <= now.time() < market_close

trader = None

def set_trader(live_trader):
    global trader
    trader = live_trader

def get_current_signals():
    """Get current strategy signals"""
    if not trader:
        return {}

    try:
        api_key = os.getenv("APCA_API_KEY_ID")
        secret_key = os.getenv("APCA_API_SECRET_KEY")
        symbol = os.getenv("SYMBOL", "SPY")

        alpaca = AlpacaConnector(api_key, secret_key)
        data = alpaca.get_historical_data(symbol, days=200)

        if data is None or len(data) == 0:
            return {}

        current_price = data['close'].iloc[-1]
        signals_info = {}

        sma_50 = data['close'].rolling(50).mean().iloc[-1]
        sma_200 = data['close'].rolling(200).mean().iloc[-1]
        sma_status = "BULLISH" if sma_50 > sma_200 else "BEARISH"

        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        rsi_status = "OVERSOLD" if current_rsi < 30 else "OVERBOUGHT" if current_rsi > 70 else "NEUTRAL"

        high_20 = data['high'].rolling(20).max().iloc[-1]
        low_20 = data['low'].rolling(20).min().iloc[-1]
        breakout_status = "ABOVE HIGH" if current_price > high_20 else "BELOW LOW" if current_price < low_20 else "NEUTRAL"

        signals_info = {
            'current_price': float(current_price),
            'sma_50': float(sma_50),
            'sma_200': float(sma_200),
            'sma_status': sma_status,
            'rsi': float(current_rsi),
            'rsi_status': rsi_status,
            'high_20': float(high_20),
            'low_20': float(low_20),
            'breakout_status': breakout_status
        }

        return signals_info
    except:
        return {}

def get_chart_data():
    """Get price data for chart"""
    try:
        api_key = os.getenv("APCA_API_KEY_ID")
        secret_key = os.getenv("APCA_API_SECRET_KEY")
        symbol = os.getenv("SYMBOL", "SPY")

        alpaca = AlpacaConnector(api_key, secret_key)
        data = alpaca.get_historical_data(symbol, days=60)

        if data is None or len(data) == 0:
            return []

        chart_data = []
        for idx, row in data.iterrows():
            timestamp = int(idx.timestamp())
            chart_data.append({
                'time': timestamp,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            })

        return chart_data
    except:
        return []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>KJO Personal Portfolio</title>
    <script src="https://unpkg.com/lightweight-charts@4/dist/lightweight-charts.standalone.production.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1600px;
            margin: 0 auto;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .header-left h1 {
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(135deg, #a78bfa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header-left p {
            color: #888;
            margin-top: 5px;
            font-size: 14px;
        }

        .header-right {
            text-align: right;
        }

        .asset-badge {
            display: inline-block;
            background: rgba(167, 139, 250, 0.1);
            border: 1px solid #a78bfa;
            color: #a78bfa;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-right: 12px;
        }

        .market-status {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            border: 1px solid;
        }

        .market-open {
            background: rgba(34, 197, 94, 0.1);
            border-color: #22c55e;
            color: #22c55e;
        }

        .market-closed {
            background: rgba(239, 68, 68, 0.1);
            border-color: #ef4444;
            color: #ef4444;
        }

        .last-update {
            color: #888;
            font-size: 12px;
            margin-top: 10px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 24px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: rgba(167, 139, 250, 0.3);
            box-shadow: 0 8px 32px rgba(167, 139, 250, 0.1);
        }

        .stat-label {
            color: #888;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }

        .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 8px;
        }

        .stat-subtitle {
            font-size: 12px;
            color: #888;
        }

        .positive {
            color: #22c55e;
        }

        .negative {
            color: #ef4444;
        }

        .signal-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 11px;
            font-weight: 600;
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .signal-bullish {
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
        }

        .signal-bearish {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }

        .signal-neutral {
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
        }

        .signal-oversold {
            background: rgba(34, 197, 94, 0.2);
            color: #22c55e;
        }

        .signal-overbought {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }

        .wide-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .section-title {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid rgba(167, 139, 250, 0.3);
            color: #a78bfa;
        }

        #chart {
            width: 100%;
            height: 400px;
            margin-bottom: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th {
            background: rgba(167, 139, 250, 0.05);
            padding: 12px;
            text-align: left;
            font-size: 12px;
            font-weight: 600;
            color: #a78bfa;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        td {
            padding: 14px 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 13px;
        }

        tr:hover {
            background: rgba(167, 139, 250, 0.05);
        }

        .button {
            background: linear-gradient(135deg, #a78bfa, #c084fc);
            color: #000;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 13px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(167, 139, 250, 0.3);
        }

        .position-item {
            background: rgba(167, 139, 250, 0.05);
            border: 1px solid rgba(167, 139, 250, 0.2);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }

        .empty-state {
            text-align: center;
            padding: 40px;
            color: #888;
        }

        .chart-container {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 24px;
            backdrop-filter: blur(10px);
            margin-bottom: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="header-left">
                <h1>KJO Personal Portfolio</h1>
                <p>Interface fully built and personalized by Kene Okonjo</p>
            </div>
            <div class="header-right">
                <div>
                    <div class="asset-badge">📊 Trading: <span id="asset-symbol">SPY</span> (US Stocks)</div>
                    <div class="market-status" id="market-status-badge">MARKET CLOSED</div>
                </div>
                <div class="last-update">Last updated: <span id="last-update">now</span></div>
                <button class="button" onclick="location.reload()" style="margin-top: 12px;">Refresh</button>
            </div>
        </div>

        <!-- Account Stats -->
        <div class="grid">
            <div class="card">
                <div class="stat-label">Account Equity</div>
                <div class="stat-value" id="equity">$0.00</div>
                <div class="stat-subtitle">Total account value</div>
            </div>
            <div class="card">
                <div class="stat-label">Available Cash</div>
                <div class="stat-value" id="cash">$0.00</div>
                <div class="stat-subtitle">Ready to trade</div>
            </div>
            <div class="card">
                <div class="stat-label">Total P&L</div>
                <div class="stat-value" id="total-pnl">$0.00</div>
                <div class="stat-subtitle">All-time performance</div>
            </div>
            <div class="card">
                <div class="stat-label">Win Rate</div>
                <div class="stat-value" id="win-rate">0%</div>
                <div class="stat-subtitle">Winning trades</div>
            </div>
        </div>

        <!-- Price Chart -->
        <div class="chart-container">
            <h2 class="section-title">Live Price Chart</h2>
            <div id="chart"></div>
        </div>

        <!-- Current Price & Signals -->
        <div class="wide-grid">
            <div class="card">
                <div class="section-title">Current Price</div>
                <div class="stat-value" id="current-price">$0.00</div>
                <div class="stat-subtitle">SPY Last Price</div>
            </div>
            <div class="card">
                <div class="section-title">Portfolio Stats</div>
                <div style="margin: 12px 0;">
                    <div style="margin-bottom: 12px;">
                        <div class="stat-label">Open Positions</div>
                        <div class="stat-value" style="font-size: 24px; color: #a78bfa;" id="open-positions">0</div>
                    </div>
                    <div>
                        <div class="stat-label">Total Trades</div>
                        <div class="stat-value" style="font-size: 24px; color: #a78bfa;" id="total-trades">0</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Strategy Signals -->
        <div style="margin-bottom: 30px;">
            <h2 class="section-title">Strategy Signals</h2>
            <div class="grid">
                <div class="card">
                    <div class="stat-label">SMA Crossover</div>
                    <div style="margin-top: 12px;">
                        <div style="margin-bottom: 8px;">
                            <span style="color: #888;">50-day:</span> <span id="sma-50">$0.00</span>
                        </div>
                        <div style="margin-bottom: 12px;">
                            <span style="color: #888;">200-day:</span> <span id="sma-200">$0.00</span>
                        </div>
                        <div class="signal-badge signal-bullish" id="sma-status-badge">NEUTRAL</div>
                    </div>
                </div>
                <div class="card">
                    <div class="stat-label">RSI Mean Reversion</div>
                    <div style="margin-top: 12px;">
                        <div style="margin-bottom: 12px;">
                            <span class="stat-value" style="font-size: 24px;" id="rsi-value">0</span>
                        </div>
                        <div class="signal-badge signal-neutral" id="rsi-status-badge">NEUTRAL</div>
                    </div>
                </div>
                <div class="card">
                    <div class="stat-label">Breakout Strategy</div>
                    <div style="margin-top: 12px;">
                        <div style="margin-bottom: 8px;">
                            <span style="color: #888;">20-day High:</span> <span id="high-20">$0.00</span>
                        </div>
                        <div style="margin-bottom: 12px;">
                            <span style="color: #888;">20-day Low:</span> <span id="low-20">$0.00</span>
                        </div>
                        <div class="signal-badge signal-neutral" id="breakout-status-badge">NEUTRAL</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Open Positions -->
        <div style="margin-bottom: 30px;">
            <h2 class="section-title">Open Positions</h2>
            <div id="positions-container" class="empty-state">No open positions</div>
        </div>

        <!-- Recent Trades -->
        <div>
            <h2 class="section-title">Recent Trades</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Strategy</th>
                        <th>Entry</th>
                        <th>Exit</th>
                        <th>Qty</th>
                        <th>P&L</th>
                        <th>Return</th>
                    </tr>
                </thead>
                <tbody id="trades-table">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        let chart;
        let candlestickSeries;

        function formatNumber(num) {
            return new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            }).format(num);
        }

        function initChart() {
            const chartContainer = document.getElementById('chart');
            chart = LightweightCharts.createChart(chartContainer, {
                layout: {
                    textColor: '#d1d5db',
                    background: { type: 'solid', color: 'transparent' },
                },
                timeScale: {
                    timeVisible: true,
                    secondsVisible: false,
                },
                grid: {
                    vertLines: { color: '#2d2d44' },
                    hLines: { color: '#2d2d44' },
                },
            });

            candlestickSeries = chart.addCandlestickSeries({
                upColor: '#22c55e',
                downColor: '#ef4444',
                borderUpColor: '#22c55e',
                borderDownColor: '#ef4444',
                wickUpColor: '#22c55e',
                wickDownColor: '#ef4444',
            });

            chart.timeScale().fitContent();
        }

        function updateChart() {
            fetch('/api/chart-data')
                .then(r => r.json())
                .then(data => {
                    if (data.chart_data && data.chart_data.length > 0) {
                        candlestickSeries.setData(data.chart_data);
                        chart.timeScale().fitContent();
                    }
                });
        }

        function loadData() {
            fetch('/api/market-status')
                .then(r => r.json())
                .then(data => {
                    const badge = document.getElementById('market-status-badge');
                    badge.textContent = data.status;
                    badge.className = 'market-status ' + (data.is_open ? 'market-open' : 'market-closed');
                });

            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('equity').textContent = '$' + formatNumber(data.equity);
                    document.getElementById('cash').textContent = '$' + formatNumber(data.cash);
                    document.getElementById('total-pnl').textContent = '$' + formatNumber(data.total_pnl);
                    document.getElementById('total-trades').textContent = data.total_trades;

                    if (data.total_trades > 0) {
                        const winRate = (data.winning_trades / data.total_trades * 100).toFixed(1);
                        document.getElementById('win-rate').textContent = winRate + '%';
                    }
                });

            fetch('/api/signals')
                .then(r => r.json())
                .then(data => {
                    if (data.current_price) {
                        document.getElementById('current-price').textContent = '$' + formatNumber(data.current_price);

                        document.getElementById('sma-50').textContent = '$' + formatNumber(data.sma_50);
                        document.getElementById('sma-200').textContent = '$' + formatNumber(data.sma_200);
                        const smaBadge = document.getElementById('sma-status-badge');
                        smaBadge.textContent = data.sma_status;
                        smaBadge.className = 'signal-badge signal-' + data.sma_status.toLowerCase();

                        document.getElementById('rsi-value').textContent = data.rsi.toFixed(1);
                        const rsiBadge = document.getElementById('rsi-status-badge');
                        rsiBadge.textContent = data.rsi_status;
                        rsiBadge.className = 'signal-badge signal-' + data.rsi_status.toLowerCase();

                        document.getElementById('high-20').textContent = '$' + formatNumber(data.high_20);
                        document.getElementById('low-20').textContent = '$' + formatNumber(data.low_20);
                        const breakoutBadge = document.getElementById('breakout-status-badge');
                        breakoutBadge.textContent = data.breakout_status;
                        breakoutBadge.className = 'signal-badge signal-' + (data.breakout_status.includes('ABOVE') ? 'bullish' : data.breakout_status.includes('BELOW') ? 'bearish' : 'neutral');
                    }
                });

            fetch('/api/positions')
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('positions-container');
                    if (data.positions && data.positions.length > 0) {
                        document.getElementById('open-positions').textContent = data.positions.length;
                        container.innerHTML = data.positions.map(pos => `
                            <div class="position-item">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                                    <div>
                                        <div class="stat-label">${pos.strategy}</div>
                                        <div class="stat-value" style="font-size: 18px;">${pos.symbol}</div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div class="stat-label">Unrealized P&L</div>
                                        <div class="stat-value" style="font-size: 18px;" class="${pos.pnl >= 0 ? 'positive' : 'negative'}">$${formatNumber(pos.pnl)}</div>
                                    </div>
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 12px;">
                                    <div><span style="color: #888;">Entry:</span> $${formatNumber(pos.entry_price)}</div>
                                    <div><span style="color: #888;">Current:</span> $${formatNumber(pos.current_price)}</div>
                                    <div><span style="color: #888;">Stop Loss:</span> $${formatNumber(pos.stop_loss)}</div>
                                    <div><span style="color: #888;">Qty:</span> ${pos.quantity}</div>
                                </div>
                            </div>
                        `).join('');
                    } else {
                        document.getElementById('open-positions').textContent = '0';
                        container.innerHTML = '<div class="empty-state">No open positions</div>';
                    }
                });

            fetch('/api/trades')
                .then(r => r.json())
                .then(data => {
                    const tbody = document.getElementById('trades-table');
                    tbody.innerHTML = '';
                    if (data.trades && data.trades.length > 0) {
                        data.trades.slice(-15).reverse().forEach(trade => {
                            const row = `<tr>
                                <td>${new Date(trade[1]).toLocaleDateString()}</td>
                                <td>${trade[2]}</td>
                                <td>$${formatNumber(trade[5])}</td>
                                <td>$${formatNumber(trade[7])}</td>
                                <td>${trade[8]}</td>
                                <td class="${trade[9] > 0 ? 'positive' : 'negative'}">$${formatNumber(trade[9])}</td>
                                <td class="${trade[10] > 0 ? 'positive' : 'negative'}">${trade[10].toFixed(2)}%</td>
                            </tr>`;
                            tbody.innerHTML += row;
                        });
                    }
                });

            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
            updateChart();
        }

        initChart();
        loadData();
        setInterval(loadData, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def get_stats():
    stats = db.get_stats()

    try:
        api_key = os.getenv("APCA_API_KEY_ID")
        secret_key = os.getenv("APCA_API_SECRET_KEY")
        alpaca = AlpacaConnector(api_key, secret_key)
        account = alpaca.get_account_info()

        if account:
            stats['cash'] = account['cash']
            stats['equity'] = account['equity']
    except:
        pass

    stats['winning_trades'] = len([t for t in db.get_all_trades() if t[9] > 0])
    return jsonify(stats)

@app.route('/api/signals')
def get_signals():
    return jsonify(get_current_signals())

@app.route('/api/positions')
def get_positions():
    if not trader:
        return jsonify({'positions': []})

    positions = []
    signals_info = get_current_signals()
    current_price = signals_info.get('current_price', 0)

    for strategy_name, pos in trader.positions.items():
        pnl = (current_price - pos['entry_price']) * pos['quantity']
        positions.append({
            'strategy': strategy_name,
            'symbol': trader.symbol,
            'entry_price': pos['entry_price'],
            'current_price': current_price,
            'stop_loss': pos['stop_loss'],
            'quantity': pos['quantity'],
            'pnl': pnl
        })

    return jsonify({'positions': positions})

@app.route('/api/trades')
def get_trades():
    trades = db.get_all_trades()
    return jsonify({'trades': trades})

@app.route('/api/market-status')
def get_market_status():
    open_status = is_market_open()
    return jsonify({
        'is_open': open_status,
        'status': 'MARKET OPEN' if open_status else 'MARKET CLOSED'
    })

@app.route('/api/chart-data')
def get_chart_data_endpoint():
    return jsonify({'chart_data': get_chart_data()})

def start_trader():
    try:
        from live_trader import LiveTrader
        global trader
        symbol = os.getenv("SYMBOL", "SPY")
        api_key = os.getenv("APCA_API_KEY_ID")
        secret_key = os.getenv("APCA_API_SECRET_KEY")

        if api_key and secret_key:
            trader = LiveTrader(symbol, api_key, secret_key)
            set_trader(trader)
            trader.start()
    except Exception as e:
        print(f"Error starting trader: {e}")

if __name__ == '__main__':
    trader_thread = threading.Thread(target=start_trader, daemon=True)
    trader_thread.start()

    port = int(os.getenv("PORT", 5000))
    print(f"Starting dashboard on port {port}...")
    app.run(debug=False, host='0.0.0.0', port=port)
