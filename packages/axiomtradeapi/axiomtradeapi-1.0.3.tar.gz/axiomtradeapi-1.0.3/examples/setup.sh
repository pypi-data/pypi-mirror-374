#!/bin/bash
# Axiom Trade Telegram Bot Setup Script
# This script helps you set up the Telegram bot with all required dependencies

echo "🤖 Axiom Trade Telegram Bot Setup"
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Install required packages
echo ""
echo "📦 Installing required packages..."
pip3 install python-telegram-bot python-dotenv

if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully"
else
    echo "❌ Failed to install packages"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo ""
    echo "📄 Creating .env file from template..."
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo "✅ .env file created from template"
        echo "⚠️  Please edit .env file with your actual values:"
        echo "   - TELEGRAM_BOT_TOKEN (get from @BotFather)"
        echo "   - TELEGRAM_CHAT_ID (your chat/channel ID)"
        echo "   - auth-access-token (from Axiom Trade)"
        echo "   - auth-refresh-token (from Axiom Trade)"
    else
        echo "❌ .env.template not found"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🧪 Testing configuration..."
python3 test_telegram_setup.py

echo ""
echo "📋 Setup Summary:"
echo "=================="
echo "✅ Python packages installed"
echo "✅ Environment file ready"
echo ""
echo "📝 Next Steps:"
echo "1. Edit .env file with your actual credentials"
echo "2. Run: python3 test_telegram_setup.py"
echo "3. If tests pass, run: python3 telegram_token_bot.py"
echo ""
echo "📖 For detailed instructions, see README.md"
echo ""
echo "🎉 Setup complete!"
