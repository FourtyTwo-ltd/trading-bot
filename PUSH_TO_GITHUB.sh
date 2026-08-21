#!/bin/bash
# Push trading bot to GitHub repository

set -e

# Configuration
REPO_URL="https://github.com/KJ-Okonjo/trading-bot.git"
BRANCH="main"

echo "🚀 Setting up Git repository..."

# Initialize git if not already done
if [ ! -d .git ]; then
    git init
    git remote add origin "$REPO_URL"
fi

# Add all files
git add -A

# Create commit
git commit -m "Initial commit: Complete automated trading bot with 3 strategies, backtesting, and live trading"

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push -u origin $BRANCH

echo "✅ Successfully pushed to GitHub!"
echo "📍 Repository: $REPO_URL"
echo "🎯 Branch: $BRANCH"
