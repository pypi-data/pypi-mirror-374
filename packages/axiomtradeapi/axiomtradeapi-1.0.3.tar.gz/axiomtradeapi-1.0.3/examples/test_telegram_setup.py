#!/usr/bin/env python3
"""
Telegram Bot Configuration Test Script

This script helps you verify that your Telegram bot and Axiom Trade API
are properly configured before running the main bot.

Usage: python test_telegram_setup.py
"""

import os
import sys
import asyncio
import dotenv

# Load environment variables
dotenv.load_dotenv()

async def test_telegram_bot():
    """Test Telegram bot connectivity"""
    print("🤖 Testing Telegram Bot Connection...")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        return False
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID not found in .env file")
        return False
    
    try:
        from telegram import Bot
        from telegram.error import TelegramError
        
        bot = Bot(token=bot_token)
        
        # Test bot connection
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: @{bot_info.username}")
        print(f"   Bot ID: {bot_info.id}")
        print(f"   Bot Name: {bot_info.first_name}")
        
        # Test sending a message
        test_message = (
            "🧪 **Test Message**\n\n"
            "✅ Your Telegram bot is configured correctly!\n"
            "🤖 Bot name: " + bot_info.first_name + "\n"
            "📡 Ready to receive Axiom Trade token alerts."
        )
        
        await bot.send_message(
            chat_id=chat_id,
            text=test_message,
            parse_mode='Markdown'
        )
        
        print(f"✅ Test message sent to chat ID: {chat_id}")
        return True
        
    except ImportError:
        print("❌ python-telegram-bot not installed")
        print("📦 Install with: pip install python-telegram-bot")
        return False
    except TelegramError as e:
        print(f"❌ Telegram error: {e}")
        if "Unauthorized" in str(e):
            print("💡 Check your bot token is correct")
        elif "chat not found" in str(e):
            print("💡 Check your chat ID is correct")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_axiom_api():
    """Test Axiom Trade API connectivity"""
    print("\n🔗 Testing Axiom Trade API Connection...")
    
    access_token = os.getenv('auth-access-token')
    refresh_token = os.getenv('auth-refresh-token')
    
    if not access_token:
        print("❌ auth-access-token not found in .env file")
        return False
    
    if not refresh_token:
        print("❌ auth-refresh-token not found in .env file")
        return False
    
    try:
        from axiomtradeapi import AxiomTradeClient
        
        # Initialize client
        client = AxiomTradeClient(
            auth_token=access_token,
            refresh_token=refresh_token
        )
        
        # Test authentication
        if client.is_authenticated():
            print("✅ Axiom Trade API authenticated successfully")
            print(f"   Access token: {access_token[:20]}...")
            print(f"   Refresh token: {refresh_token[:20]}...")
            return True
        else:
            print("❌ Axiom Trade API authentication failed")
            print("💡 Check your tokens are valid and not expired")
            return False
            
    except ImportError:
        print("❌ axiomtradeapi not found")
        print("💡 Make sure you're running from the correct directory")
        return False
    except Exception as e:
        print(f"❌ Axiom API error: {e}")
        return False

def test_environment_file():
    """Test .env file exists and has required variables"""
    print("📄 Testing Environment Configuration...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("💡 Copy .env.template to .env and fill in your values")
        return False
    
    print("✅ .env file found")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID', 
        'auth-access-token',
        'auth-refresh-token'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif value.strip() in ['your_telegram_bot_token_here', 'your_chat_id_here', 
                              'your_axiom_access_token_here', 'your_axiom_refresh_token_here']:
            missing_vars.append(var + " (placeholder value)")
    
    if missing_vars:
        print("❌ Missing or placeholder values:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ All required environment variables are set")
    return True

async def main():
    """Main test function"""
    print("🧪 Axiom Trade Telegram Bot Configuration Test")
    print("=" * 55)
    
    all_tests_passed = True
    
    # Test 1: Environment file
    if not test_environment_file():
        all_tests_passed = False
    
    # Test 2: Axiom Trade API
    if not test_axiom_api():
        all_tests_passed = False
    
    # Test 3: Telegram Bot
    if not await test_telegram_bot():
        all_tests_passed = False
    
    print("\n" + "=" * 55)
    
    if all_tests_passed:
        print("🎉 All tests passed! Your bot is ready to run.")
        print("🚀 Start the bot with: python telegram_token_bot.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("📖 Check the README.md for detailed setup instructions.")
    
    print("=" * 55)

if __name__ == "__main__":
    asyncio.run(main())
