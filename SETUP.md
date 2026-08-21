# Setup Guide - Step by Step

## Step 1: Install Dependencies

```bash
cd ~/trading-bot
pip install -r requirements.txt
```

Takes about 2 minutes. This installs all Python libraries needed.

## Step 2: Get Alpaca API Credentials

**This is the most important step.**

1. Go to **https://app.alpaca.markets/**
2. Click "Sign Up" (free account)
3. Complete registration
4. In dashboard, go to **Settings → API Keys**
5. Click "Create New Key"
6. Copy the **Key ID** and **Secret Key**

**⚠️ Important:** 
- This is paper trading (fake money) - totally free
- Keep your secret key private (don't share it)
- Default mode is paper trading (you can toggle it in settings)

## Step 3: Create .env File

```bash
cd ~/trading-bot
cp .env.example .env
nano .env
```

Paste your credentials:
```
APCA_API_KEY_ID=your_key_here
APCA_API_SECRET_KEY=your_secret_here
```

Save and exit (Ctrl+X, then Y, then Enter if using nano)

## Step 4: Test Connection

```bash
python
```

```python
from alpaca_connector import AlpacaConnector
c = AlpacaConnector()
print(c.get_account_info())
```

You should see your account info. If error, check credentials.

## Step 5: Backtest (RECOMMENDED)

```bash
python run_backtest.py
```

This tests all 3 strategies on past data. You'll see:
- How many trades each strategy would have made
- How profitable they were
- Win rate

**This is important** - tells you if strategies actually work before going live.

## Step 6: Start Live Trading

```bash
python main.py
```

This starts:
1. The live trading bot (monitors market)
2. The dashboard (http://localhost:5000)

Open browser and go to http://localhost:5000 to watch it.

## Step 7: Monitor

- Dashboard shows live stats
- Check it daily
- You can close terminal anytime (bot runs independently)
- To stop, press Ctrl+C

## Common Issues

**"No module named 'alpaca'"**
- Run: `pip install -r requirements.txt`

**"API credentials not found"**
- Make sure .env file exists
- Make sure credentials are correct

**No trades happening**
- Check if market is open (9:30am - 4pm ET, weekdays only)
- Run backtest to see if strategies work
- Check dashboard console for errors

## What's Next?

After running for a few days/weeks:
1. Check performance in dashboard
2. Review trades in database
3. Adjust if needed
4. Consider adding more strategies

That's it! The bot handles everything else automatically.
