# 🤖 Automated Trading Bot

A complete automated trading system for backtesting and paper trading with Alpaca. Includes 3 independent trading strategies, comprehensive logging, and a real-time dashboard.

## 📋 Features

✅ **3 Independent Trading Strategies**
- Simple Moving Average Crossover (SMA)
- RSI Mean Reversion
- Breakout Strategy

✅ **Risk Management**
- 1% max risk per trade
- 3% max daily loss limit
- Position sizing based on stop loss
- Real-time stop loss monitoring

✅ **Paper Trading**
- Alpaca API integration
- Free paper trading account
- Real-time market data
- Automatic order execution

✅ **Comprehensive Logging**
- Every signal logged
- Every trade logged (entry, exit, P&L)
- Daily performance stats
- Complete trade history in database

✅ **Real-Time Dashboard**
- View live stats
- Recent trades
- Win rate and P&L
- Auto-refresh every 30 seconds

✅ **Backtesting**
- Test strategies on historical data
- Performance metrics
- Identify profitable strategies before live trading

## 🚀 Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your Alpaca credentials
nano .env
```

### 2. Get Alpaca API Credentials

1. Go to https://app.alpaca.markets/
2. Sign up for a free account
3. Get your API Key ID and Secret Key
4. Paste them in `.env` file

**Important:** Use PAPER TRADING account (default). This is free and uses fake money.

### 3. Backtest First (Recommended)

```bash
# Test all 3 strategies on historical data
python run_backtest.py
```

This shows you:
- How many trades each strategy would make
- Win rate and profitability
- If the strategy is actually profitable before using real paper trading

### 4. Start Live Trading

```bash
# Start the bot and dashboard
python main.py
```

This will:
- Start the live trader (monitors market during hours)
- Start the dashboard on http://localhost:5000
- Execute trades automatically when conditions are met
- Log everything to database

Open http://localhost:5000 in your browser to watch it live.

## 📊 How It Works

1. **Continuous Monitoring** - Bot checks market every hour during trading hours
2. **Strategy Evaluation** - Each strategy evaluates current price/indicators
3. **Signal Generation** - If entry conditions met, generates BUY signal
4. **Order Execution** - Automatically places buy order via Alpaca API
5. **Trade Tracking** - Every trade logged to database
6. **Exit Management** - Bot watches for exit signals or stop loss

## 📈 Understanding Results

**Win Rate** - % of trades that made money
- Target: > 50%

**Average Return/Trade** - Average profit per trade
- Target: Positive

**Total P&L** - Total profit/loss
- Should be positive over time

**Max Daily Loss** - System stops trading if daily loss exceeds 3%
- Protects capital on bad days

## ⚙️ Strategies Explained

### SMA Crossover
- **Entry:** When 50-day average crosses above 200-day average (trend starting)
- **Exit:** When price drops below 50-day average (trend ending)
- **Best For:** Trending markets

### RSI Mean Reversion
- **Entry:** When RSI < 30 (oversold = bounce coming)
- **Exit:** When RSI > 70 (overbought = pullback coming)
- **Best For:** Bouncy/choppy markets

### Breakout
- **Entry:** When price breaks above 20-day high
- **Exit:** When price closes below 20-day low
- **Best For:** Momentum/breakout moves

## 💾 Data & Logs

- `trades.db` - Complete trade history
- `backtest.db` - Backtest results
- Dashboard at http://localhost:5000 - Real-time stats

## ⚠️ Important Notes

1. **Paper Trading Only** - No real money at risk
2. **Test First** - Always backtest strategies before going live
3. **Monitor Daily** - Check dashboard to ensure system is working
4. **Market Hours** - Bot only trades during market hours (9:30am - 4pm ET)
5. **Realistic Expectations** - 50% win rate = success. Don't expect 100%

## 🔧 Troubleshooting

**"API credentials not found"**
- Make sure .env file exists and has your credentials

**"No data available"**
- Check internet connection
- Verify Alpaca API credentials are correct
- Make sure market is open

**No trades being executed**
- Check if market is open (9:30am - 4pm ET weekdays)
- Run backtest first to see if strategies generate signals
- Check dashboard for strategy evaluations

## 📞 Support

Check database for detailed logs:
```bash
sqlite3 trades.db
SELECT * FROM trades;
SELECT * FROM signals;
```

## 📝 Next Steps

1. ✅ Set up credentials in .env
2. ✅ Run backtest to validate strategies
3. ✅ Start live trader
4. ✅ Monitor dashboard
5. ✅ Check performance after 1-2 weeks
6. ✅ Consider adding more strategies if needed

Good luck! Remember: positive expectancy over time = success.
