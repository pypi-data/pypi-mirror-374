#!/usr/bin/env python3
"""
Simple Telegram Bot Demo for Axiom Trade

This is a simplified version of the main bot that demonstrates
the message formatting and basic functionality without requiring
the full WebSocket implementation.

Use this for testing message formatting and Telegram connectivity.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

try:
    from telegram import Bot
    from telegram.error import TelegramError
except ImportError:
    print("❌ Error: python-telegram-bot not installed")
    print("📦 Install with: pip install python-telegram-bot")
    sys.exit(1)

try:
    import dotenv
except ImportError:
    print("❌ Error: python-dotenv not installed")
    print("📦 Install with: pip install python-dotenv")
    sys.exit(1)

# Load environment variables
dotenv.load_dotenv()

class SimpleTelegramDemo:
    """Simple demo bot for testing Telegram integration"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            print("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env")
            sys.exit(1)
        
        self.bot = Bot(token=self.bot_token)
    
    def create_sample_token_data(self):
        """Create sample token data for demonstration"""
        return {
            'content': {
                'token_name': 'MemeCoin',
                'token_ticker': 'MEME',
                'token_address': 'AbC123dEf456gHi789jKl012mNo345pQr678sTu901vWx234yZ567',
                'created_at': '2024-01-15T10:30:00Z',
                'initial_liquidity_sol': 10.5,
                'supply': 1000000000,
                'dev_holds_percent': 5.67,
                'top_10_holders': 15.23,
                'lp_burned': 100,
                'twitter': 'https://twitter.com/memecoin',
                'telegram': 'https://t.me/memecoin',
                'website': 'https://memecoin.fun',
                'protocol': 'Pump.fun',
                'deployer_address': 'Dev123AbC456dEf789gHi012jKl345mNo678pQr901'
            }
        }
    
    def format_token_message(self, token_data):
        """Format sample token data into Telegram message"""
        content = token_data.get('content', {})
        
        token_name = content.get('token_name', 'Unknown Token')
        token_ticker = content.get('token_ticker', 'N/A')
        token_address = content.get('token_address', 'N/A')
        
        # Calculate sample metrics
        initial_liquidity_sol = content.get('initial_liquidity_sol', 0)
        supply = content.get('supply', 0)
        dev_holds_percent = content.get('dev_holds_percent', 0)
        top_10_holders = content.get('top_10_holders', 0)
        
        estimated_fdv = initial_liquidity_sol * 2 * (supply / 1000000) if supply > 0 else 0
        
        # Extract social links
        twitter = content.get('twitter', '')
        telegram = content.get('telegram', '')
        website = content.get('website', '')
        protocol = content.get('protocol', 'Unknown')
        deployer = content.get('deployer_address', 'N/A')
        
        # Format the message (same as main bot)
        message = f"💊 **{token_name}** / {token_ticker}\n\n"
        
        message += f"💰 **FDV**: ${estimated_fdv:,.2f}\n"
        message += f"🌊 **Volume**: ${initial_liquidity_sol * 2:,.2f} USD\n"
        message += f"👥 **Holders**: {137}\n"
        message += f"⚫ **Top 10**: {top_10_holders:.2f}%\n"
        message += f"📦 **Bundle**: {0:.2f}%\n"
        message += f"🧑‍💻 **Dev**: {dev_holds_percent:.2f}%\n"
        message += f"🎯 **Snipers**: 1\n\n"
        
        message += f"⏰ **Token Age**: 5m\n\n"
        
        message += f"🔗 **Links**:\n"
        message += f"👨‍💻 **Dev**: `{deployer[:20]}...`\n"
        
        if twitter:
            message += f"🐦 **Twitter**: [Link]({twitter})\n"
        if telegram:
            message += f"💬 **Telegram**: [Link]({telegram})\n"
        if website:
            message += f"🌐 **Website**: [Link]({website})\n"
        
        message += f"\n`{token_address}`\n"
        message += f"\n🏭 **Protocol**: {protocol}"
        
        return message
    
    async def send_demo_messages(self):
        """Send demonstration messages"""
        try:
            # Send welcome message
            welcome_msg = (
                "🧪 **Telegram Bot Demo Mode**\n\n"
                "This is a demonstration of the Axiom Trade token monitor formatting.\n"
                "The actual bot will send real-time token data from the WebSocket feed.\n\n"
                "📱 Sample token alert coming up..."
            )
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=welcome_msg,
                parse_mode='Markdown'
            )
            
            print("✅ Welcome message sent")
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Send sample token alert
            sample_data = self.create_sample_token_data()
            token_message = self.format_token_message(sample_data)
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=token_message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            print("✅ Sample token alert sent")
            
            # Send completion message
            await asyncio.sleep(2)
            
            completion_msg = (
                "✅ **Demo Complete**\n\n"
                "🎯 Message formatting is working correctly!\n"
                "🚀 Your bot is ready for the full implementation.\n\n"
                "📖 Run `python telegram_token_bot.py` for live monitoring."
            )
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=completion_msg,
                parse_mode='Markdown'
            )
            
            print("✅ Demo completed successfully")
            
        except TelegramError as e:
            print(f"❌ Telegram error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

async def main():
    """Main demo function"""
    print("🧪 Axiom Trade Telegram Bot Demo")
    print("=" * 40)
    
    try:
        demo = SimpleTelegramDemo()
        
        # Test bot connection
        bot_info = await demo.bot.get_me()
        print(f"🤖 Bot connected: @{bot_info.username}")
        
        # Send demo messages
        await demo.send_demo_messages()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
