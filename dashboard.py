from flask import Flask, jsonify, render_template_string
from database import TradeDatabase
import pandas as pd

app = Flask(__name__)
db = TradeDatabase("trades.db")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Trading Bot Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #333; color: white; padding: 20px; border-radius: 5px; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
        .stat-card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-value { font-size: 28px; font-weight: bold; color: #333; }
        .stat-label { color: #888; font-size: 14px; margin-top: 5px; }
        .positive { color: #27ae60; }
        .negative { color: #e74c3c; }
        table { width: 100%; border-collapse: collapse; background: white; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f9f9f9; font-weight: bold; }
        tr:hover { background: #f5f5f5; }
        .refresh-btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .refresh-btn:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Trading Bot Dashboard</h1>
            <p>Real-time monitoring for automated trading strategies</p>
        </div>

        <button class="refresh-btn" onclick="location.reload()">Refresh Data</button>

        <div class="stats" id="stats-container">
            <div class="stat-card">
                <div class="stat-label">Total Trades</div>
                <div class="stat-value" id="total-trades">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Win Rate</div>
                <div class="stat-value" id="win-rate">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total P&L</div>
                <div class="stat-value" id="total-pnl">$0.00</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Return/Trade</div>
                <div class="stat-value" id="avg-return">0%</div>
            </div>
        </div>

        <h2>Recent Trades</h2>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Strategy</th>
                    <th>Symbol</th>
                    <th>Entry</th>
                    <th>Exit</th>
                    <th>Qty</th>
                    <th>P&L</th>
                    <th>Return %</th>
                </tr>
            </thead>
            <tbody id="trades-table">
            </tbody>
        </table>
    </div>

    <script>
        function loadData() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('total-trades').textContent = data.total_trades;
                    document.getElementById('total-pnl').textContent = '$' + data.total_pnl.toFixed(2);
                    document.getElementById('avg-return').textContent = data.avg_return_pct.toFixed(2) + '%';

                    if (data.total_trades > 0) {
                        const winRate = (data.winning_trades / data.total_trades * 100).toFixed(2);
                        document.getElementById('win-rate').textContent = winRate + '%';
                    }
                });

            fetch('/api/trades')
                .then(r => r.json())
                .then(data => {
                    const tbody = document.getElementById('trades-table');
                    tbody.innerHTML = '';
                    data.slice(-20).reverse().forEach(trade => {
                        const row = `<tr>
                            <td>${new Date(trade[1]).toLocaleDateString()}</td>
                            <td>${trade[2]}</td>
                            <td>${trade[3]}</td>
                            <td>$${trade[5].toFixed(2)}</td>
                            <td>$${trade[7].toFixed(2)}</td>
                            <td>${trade[8]}</td>
                            <td class="${trade[9] > 0 ? 'positive' : 'negative'}">$${trade[9].toFixed(2)}</td>
                            <td class="${trade[10] > 0 ? 'positive' : 'negative'}">${trade[10].toFixed(2)}%</td>
                        </tr>`;
                        tbody.innerHTML += row;
                    });
                });
        }

        loadData();
        setInterval(loadData, 30000);  // Refresh every 30 seconds
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
    stats['winning_trades'] = len([t for t in db.get_all_trades() if t[9] > 0])
    return jsonify(stats)

@app.route('/api/trades')
def get_trades():
    trades = db.get_all_trades()
    return jsonify(trades)

if __name__ == '__main__':
    print("Starting dashboard on http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
