# Deploying to Render.com

This trading bot is configured to run on Render.com - a free cloud hosting platform.

## Why Render?

✅ **No terminal on your machine**  
✅ **Runs 24/7** - bot trades even when your laptop is off  
✅ **New laptop?** - Nothing to install, bot already in cloud  
✅ **Just check dashboard** - Access from any browser  

---

## Deployment Steps

### 1. Connect GitHub to Render

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Select "Connect a repository"
4. Choose **fourtytwo-ltd/trading-bot**
5. Click "Connect"

### 2. Configure Deployment

On the Render page, fill in:

- **Name**: `trading-bot` (or any name you like)
- **Runtime**: Python 3.11
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python dashboard.py`
- **Plan**: Free (or paid for better uptime)

### 3. Add Environment Variables

Click "Advanced" and add these environment variables:

```
APCA_API_KEY_ID = PKJWZ5SVOBQIKSGMVJKWPURLEJ
APCA_API_SECRET_KEY = HaqQAuhN1pTxFqwmStvKWDSjFpxDHWaVb7u77CiKeNHA
SYMBOL = SPY
EVALUATION_INTERVAL = 60
INITIAL_CAPITAL = 500
```

(These are already in your GitHub .env file, but Render needs them as env vars)

### 4. Click "Create Web Service"

Render will:
- Clone your GitHub repo
- Install dependencies
- Start the bot
- Assign you a URL like `trading-bot-xxxxx.onrender.com`

Takes about 2-3 minutes.

### 5. Access Your Dashboard

Once deployed, go to: **https://trading-bot-xxxxx.onrender.com**

You'll see the live dashboard with:
- Real-time stats
- Recent trades
- Win rate and P&L
- Auto-refreshes every 30 seconds

---

## What's Happening

**In the cloud:**
- Dashboard (Flask server) running on Render
- Live Trader running in background, monitoring market
- Database (trades.db) storing all trades
- Automatically evaluates strategies every hour

**You do:**
- Open browser
- Check dashboard
- That's it

---

## Common Questions

**Q: Does it trade when I close my laptop?**  
A: Yes! The bot runs in the cloud 24/7, independent of your machine.

**Q: What if I get a new laptop?**  
A: Nothing changes. The bot is already running in the cloud. Just go to your Render dashboard link.

**Q: How much does it cost?**  
A: Free tier is fine (with some limitations). Paid tier is ~$7/month for better uptime.

**Q: Can I see the trades?**  
A: Yes, open the dashboard link. It shows all trades, P&L, win rate, everything.

**Q: What if something goes wrong?**  
A: Check the Render logs (Dashboard → Logs). You can restart the service from Render dashboard.

---

## Monitoring

Once deployed:
1. Save your Render dashboard link: `https://trading-bot-xxxxx.onrender.com`
2. Check it daily (or whenever you want)
3. You can also check Render logs if needed

That's it! Your bot is now running 24/7 in the cloud.
