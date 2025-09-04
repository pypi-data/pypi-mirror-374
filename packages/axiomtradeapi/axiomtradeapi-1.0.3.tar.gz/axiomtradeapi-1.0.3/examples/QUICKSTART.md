# 🚀 Quick Start Guide - Telegram Token Bot

This guide will get your Telegram bot up and running in 5 minutes!

## 📱 Step 1: Create Your Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a name for your bot (e.g., "My Token Monitor")
4. Choose a username ending in "bot" (e.g., "mytokenmonitor_bot")
5. **Save the bot token** (looks like `123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## 🆔 Step 2: Get Your Chat ID

**Option A - Personal Messages:**
1. Message [@userinfobot](https://t.me/userinfobot)
2. It will reply with your user ID (e.g., `123456789`)

**Option B - Channel/Group:**
1. Add your bot to the channel/group as admin
2. Send a test message
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find your channel/group ID in the response

## ⚙️ Step 3: Quick Setup

```bash
# Navigate to examples folder
cd examples

# Run the setup script (installs dependencies)
./setup.sh

# Edit your configuration
nano .env
```

In `.env`, replace the placeholder values:
```env
TELEGRAM_BOT_TOKEN=123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
auth-access-token=your_axiom_access_token
auth-refresh-token=your_axiom_refresh_token
```

## 🧪 Step 4: Test Everything

```bash
# Test your configuration
python3 test_telegram_setup.py

# Try the demo bot (sends sample messages)
python3 telegram_bot_demo.py
```

## 🚀 Step 5: Run the Live Bot

```bash
# Start monitoring for real tokens
python3 telegram_token_bot.py
```

You should see:
- ✅ Bot startup message in Telegram
- 📡 WebSocket connection established
- 💊 Real-time token alerts

## 🔧 Troubleshooting

**"Import telegram could not be resolved":**
```bash
pip3 install python-telegram-bot
```

**"Bot token invalid":**
- Double-check the token from @BotFather
- Ensure no extra spaces in .env file

**"Chat not found":**
- Verify your chat ID is correct
- For channels, make sure bot is added as admin

**"Axiom authentication failed":**
- Check your access/refresh tokens are valid
- Copy fresh tokens from your working .env

## 📊 What You'll See

The bot sends messages like this:

```
💊 **MemeCoin** / MEME

💰 FDV: $21,000.00
🌊 Volume: $21.00 USD
👥 Holders: 137
⚫ Top 10: 15.23%
🧑‍💻 Dev: 5.67%

⏰ Token Age: 5m

🔗 Links:
🐦 Twitter: [Link](https://twitter.com/...)
💬 Telegram: [Link](https://t.me/...)

`TokenAddress123...`

🏭 Protocol: Pump.fun
```

## 🎯 Success!

Your bot is now monitoring new Solana tokens and sending alerts to your Telegram! 🎉

Need help? Check the full [README.md](README.md) for detailed documentation.
