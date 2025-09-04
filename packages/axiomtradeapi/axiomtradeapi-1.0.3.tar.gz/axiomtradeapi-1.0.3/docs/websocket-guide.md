---
layout: guide
title: "WebSocket Integration Guide - Real-Time Solana Data"
description: "Complete guide to real-time Solana token monitoring and WebSocket streaming using AxiomTradeAPI-py for building advanced trading bots."
difficulty: "Intermediate"
estimated_time: "30 minutes"
---

# WebSocket Integration Guide - AxiomTradeAPI-py | Real-Time Solana Trading Data

## Complete Guide to Real-Time Solana Token Monitoring and WebSocket Streaming

Master real-time data streaming with **AxiomTradeAPI-py**, the most advanced Python SDK for Solana WebSocket integration. Build powerful trading bots, token snipers, and market monitoring systems with millisecond-latency data feeds from Axiom Trade.

## 🚀 Quick Start: Real-Time Token Monitoring

### Basic WebSocket Setup

Start receiving live token updates in under 5 minutes:

```python
import asyncio
from axiomtradeapi import AxiomTradeClient

# Your authentication tokens (get from browser cookies)
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
REFRESH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

async def handle_new_tokens(tokens):
    """Process incoming token updates"""
    for token in tokens:
        print(f"🚨 NEW TOKEN ALERT!")
        print(f"   Name: {token['tokenName']} ({token['tokenTicker']})")
        print(f"   Address: {token['tokenAddress']}")
        print(f"   Market Cap: {token['marketCapSol']} SOL")
        print(f"   Volume: {token['volumeSol']} SOL")
        print(f"   Protocol: {token['protocol']}")
        print("-" * 50)

async def main():
    # Initialize authenticated client
    client = AxiomTradeClient(
        auth_token=AUTH_TOKEN,
        refresh_token=REFRESH_TOKEN
    )
    
    # Subscribe to new token pairs
    await client.subscribe_new_tokens(handle_new_tokens)
    
    print("🔄 Listening for new tokens... (Press Ctrl+C to stop)")
    
    # Start the WebSocket listener
    await client.ws.start()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🏆 Advanced WebSocket Applications

### 1. Intelligent Token Sniper Bot

Build an automated token sniper that filters and acts on new tokens:

```python
import asyncio
import logging
from datetime import datetime
from axiomtradeapi import AxiomTradeClient

class TokenSniperBot:
    def __init__(self, auth_token, refresh_token):
        self.client = AxiomTradeClient(
            auth_token=auth_token,
            refresh_token=refresh_token,
            log_level=logging.INFO
        )
        
        # Sniper configuration
        self.min_market_cap = 10.0      # Minimum 10 SOL market cap
        self.max_market_cap = 1000.0    # Maximum 1000 SOL market cap
        self.min_volume = 5.0           # Minimum 5 SOL volume
        self.target_protocols = ["Raydium", "Orca", "Jupiter"]
        
        # Tracking
        self.sniped_tokens = []
        self.processed_tokens = set()
        
        self.setup_logging()
    
    def setup_logging(self):
        """Setup comprehensive logging for token sniper"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('token_sniper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def meets_sniper_criteria(self, token):
        """Check if token meets our sniping criteria"""
        
        # Avoid duplicate processing
        if token['tokenAddress'] in self.processed_tokens:
            return False
        
        self.processed_tokens.add(token['tokenAddress'])
        
        market_cap = token.get('marketCapSol', 0)
        volume = token.get('volumeSol', 0)
        protocol = token.get('protocol', '')
        
        # Market cap filter
        if not (self.min_market_cap <= market_cap <= self.max_market_cap):
            self.logger.debug(f"❌ {token['tokenName']}: Market cap {market_cap} SOL outside range")
            return False
        
        # Volume filter
        if volume < self.min_volume:
            self.logger.debug(f"❌ {token['tokenName']}: Volume {volume} SOL too low")
            return False
        
        # Protocol filter
        if protocol not in self.target_protocols:
            self.logger.debug(f"❌ {token['tokenName']}: Protocol {protocol} not in targets")
            return False
        
        # Additional quality checks
        if not self.quality_checks(token):
            return False
        
        return True
    
    def quality_checks(self, token):
        """Advanced quality checks for token legitimacy"""
        
        # Check for suspicious patterns
        name = token.get('tokenName', '').lower()
        ticker = token.get('tokenTicker', '').lower()
        
        # Avoid obvious scams
        scam_keywords = ['elon', 'musk', 'doge', 'shib', 'safemoon', 'free', 'airdrop']
        if any(keyword in name or keyword in ticker for keyword in scam_keywords):
            self.logger.warning(f"⚠️ {token['tokenName']}: Contains suspicious keywords")
            return False
        
        # Check for reasonable name/ticker length
        if len(name) > 50 or len(ticker) > 10:
            self.logger.warning(f"⚠️ {token['tokenName']}: Name/ticker too long")
            return False
        
        # Check for social media presence (positive indicator)
        has_socials = any([
            token.get('website'),
            token.get('twitter'),
            token.get('telegram')
        ])
        
        if not has_socials:
            self.logger.info(f"⚠️ {token['tokenName']}: No social media presence")
            # Don't reject, but note it
        
        return True
    
    async def execute_snipe(self, token):
        """Execute the sniping action for a qualified token"""
        
        self.logger.info(f"🎯 SNIPING TOKEN: {token['tokenName']}")
        
        snipe_data = {
            'timestamp': datetime.now().isoformat(),
            'token_name': token['tokenName'],
            'token_ticker': token['tokenTicker'],
            'token_address': token['tokenAddress'],
            'market_cap_sol': token['marketCapSol'],
            'volume_sol': token['volumeSol'],
            'protocol': token['protocol'],
            'website': token.get('website'),
            'twitter': token.get('twitter'),
            'telegram': token.get('telegram')
        }
        
        self.sniped_tokens.append(snipe_data)
        
        # Here you would implement actual trading logic:
        # - Calculate position size
        # - Execute buy order
        # - Set stop-loss/take-profit
        # - Record transaction
        
        # For demo, we'll just log and save
        self.save_sniped_token(snipe_data)
        
        # Send notifications
        await self.send_snipe_notification(snipe_data)
    
    def save_sniped_token(self, snipe_data):
        """Save sniped token data to file"""
        import json
        
        try:
            with open('sniped_tokens.json', 'r') as f:
                sniped_list = json.load(f)
        except FileNotFoundError:
            sniped_list = []
        
        sniped_list.append(snipe_data)
        
        with open('sniped_tokens.json', 'w') as f:
            json.dump(sniped_list, f, indent=2)
        
        self.logger.info(f"💾 Saved snipe data for {snipe_data['token_name']}")
    
    async def send_snipe_notification(self, snipe_data):
        """Send notifications about successful snipes"""
        
        # Discord webhook notification
        await self.send_discord_notification(snipe_data)
        
        # Telegram notification
        await self.send_telegram_notification(snipe_data)
        
        # Email notification
        self.send_email_notification(snipe_data)
    
    async def send_discord_notification(self, snipe_data):
        """Send Discord webhook notification"""
        import aiohttp
        
        webhook_url = "YOUR_DISCORD_WEBHOOK_URL"  # Replace with your webhook
        
        embed = {
            "title": "🎯 Token Sniped!",
            "description": f"Successfully identified and sniped {snipe_data['token_name']}",
            "color": 0x00ff00,
            "fields": [
                {"name": "Token", "value": f"{snipe_data['token_name']} ({snipe_data['token_ticker']})", "inline": True},
                {"name": "Market Cap", "value": f"{snipe_data['market_cap_sol']} SOL", "inline": True},
                {"name": "Volume", "value": f"{snipe_data['volume_sol']} SOL", "inline": True},
                {"name": "Protocol", "value": snipe_data['protocol'], "inline": True},
                {"name": "Address", "value": snipe_data['token_address'], "inline": False}
            ],
            "timestamp": snipe_data['timestamp']
        }
        
        payload = {"embeds": [embed]}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 204:
                        self.logger.info("📱 Discord notification sent")
                    else:
                        self.logger.error(f"❌ Discord notification failed: {response.status}")
        except Exception as e:
            self.logger.error(f"❌ Discord notification error: {e}")
    
    async def send_telegram_notification(self, snipe_data):
        """Send Telegram notification"""
        import aiohttp
        
        bot_token = "YOUR_TELEGRAM_BOT_TOKEN"  # Replace with your bot token
        chat_id = "YOUR_CHAT_ID"               # Replace with your chat ID
        
        message = f"""
🎯 *Token Sniped!*

*Token:* {snipe_data['token_name']} ({snipe_data['token_ticker']})
*Market Cap:* {snipe_data['market_cap_sol']} SOL
*Volume:* {snipe_data['volume_sol']} SOL
*Protocol:* {snipe_data['protocol']}
*Address:* `{snipe_data['token_address']}`

Time: {snipe_data['timestamp']}
        """
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        self.logger.info("📱 Telegram notification sent")
                    else:
                        self.logger.error(f"❌ Telegram notification failed: {response.status}")
        except Exception as e:
            self.logger.error(f"❌ Telegram notification error: {e}")
    
    def send_email_notification(self, snipe_data):
        """Send email notification"""
        import smtplib
        from email.mime.text import MimeText
        from email.mime.multipart import MimeMultipart
        
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        email_username = "your-email@gmail.com"
        email_password = "your-app-password"
        to_email = "alerts@your-domain.com"
        
        subject = f"Token Sniped: {snipe_data['token_name']}"
        
        body = f"""
Token Sniper Alert!

A new token has been successfully identified and sniped:

Token Details:
- Name: {snipe_data['token_name']} ({snipe_data['token_ticker']})
- Address: {snipe_data['token_address']}
- Market Cap: {snipe_data['market_cap_sol']} SOL
- Volume: {snipe_data['volume_sol']} SOL
- Protocol: {snipe_data['protocol']}

Social Media:
- Website: {snipe_data.get('website', 'N/A')}
- Twitter: {snipe_data.get('twitter', 'N/A')}
- Telegram: {snipe_data.get('telegram', 'N/A')}

Timestamp: {snipe_data['timestamp']}

Happy trading!
        """
        
        try:
            msg = MimeMultipart()
            msg['From'] = email_username
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_username, email_password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info("📧 Email notification sent")
        except Exception as e:
            self.logger.error(f"❌ Email notification error: {e}")
    
    async def process_new_tokens(self, tokens):
        """Main token processing function"""
        
        self.logger.info(f"📡 Received {len(tokens)} new tokens")
        
        for token in tokens:
            try:
                if self.meets_sniper_criteria(token):
                    self.logger.info(f"✅ Token qualifies for sniping: {token['tokenName']}")
                    await self.execute_snipe(token)
                else:
                    self.logger.debug(f"⏭️ Token filtered out: {token['tokenName']}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error processing token {token.get('tokenName', 'Unknown')}: {e}")
    
    async def start_sniping(self):
        """Start the token sniping bot"""
        
        self.logger.info("🎯 Starting Token Sniper Bot...")
        self.logger.info(f"📊 Criteria:")
        self.logger.info(f"   Market Cap: {self.min_market_cap} - {self.max_market_cap} SOL")
        self.logger.info(f"   Min Volume: {self.min_volume} SOL")
        self.logger.info(f"   Target Protocols: {', '.join(self.target_protocols)}")
        
        try:
            # Subscribe to new tokens
            await self.client.subscribe_new_tokens(self.process_new_tokens)
            
            # Start listening
            await self.client.ws.start()
            
        except KeyboardInterrupt:
            self.logger.info("👋 Token sniper stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Fatal error in token sniper: {e}")
            raise
    
    def get_sniper_stats(self):
        """Get sniping statistics"""
        return {
            "total_processed": len(self.processed_tokens),
            "total_sniped": len(self.sniped_tokens),
            "success_rate": len(self.sniped_tokens) / len(self.processed_tokens) * 100 if self.processed_tokens else 0
        }

# Usage
async def main():
    # Initialize sniper bot
    sniper = TokenSniperBot(
        auth_token="your-auth-token",
        refresh_token="your-refresh-token"
    )
    
    # Start sniping
    await sniper.start_sniping()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Market Sentiment Analyzer

Analyze token sentiment and market trends in real-time:

```python
import asyncio
import json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from axiomtradeapi import AxiomTradeClient

class MarketSentimentAnalyzer:
    def __init__(self, auth_token, refresh_token):
        self.client = AxiomTradeClient(
            auth_token=auth_token,
            refresh_token=refresh_token
        )
        
        # Data storage
        self.token_data = defaultdict(list)
        self.market_metrics = {
            'new_tokens_per_hour': deque(maxlen=24),  # 24 hour window
            'protocol_distribution': defaultdict(int),
            'market_cap_trends': deque(maxlen=100),
            'volume_trends': deque(maxlen=100)
        }
        
        # Analysis configuration
        self.analysis_interval = 3600  # 1 hour
        self.last_analysis = datetime.now()
    
    async def process_market_data(self, tokens):
        """Process incoming token data for market analysis"""
        
        current_time = datetime.now()
        
        for token in tokens:
            # Store token data
            token_entry = {
                'timestamp': current_time.isoformat(),
                'name': token['tokenName'],
                'ticker': token['tokenTicker'],
                'address': token['tokenAddress'],
                'market_cap': token['marketCapSol'],
                'volume': token['volumeSol'],
                'protocol': token['protocol']
            }
            
            self.token_data[token['tokenAddress']].append(token_entry)
            
            # Update metrics
            self.market_metrics['protocol_distribution'][token['protocol']] += 1
            self.market_metrics['market_cap_trends'].append(token['marketCapSol'])
            self.market_metrics['volume_trends'].append(token['volumeSol'])
        
        # Update tokens per hour
        self.market_metrics['new_tokens_per_hour'].append({
            'timestamp': current_time.isoformat(),
            'count': len(tokens)
        })
        
        # Perform analysis if interval elapsed
        if current_time - self.last_analysis >= timedelta(seconds=self.analysis_interval):
            await self.perform_market_analysis()
            self.last_analysis = current_time
    
    async def perform_market_analysis(self):
        """Perform comprehensive market sentiment analysis"""
        
        print("\n📊 MARKET SENTIMENT ANALYSIS")
        print("=" * 50)
        
        # Analyze token velocity
        self.analyze_token_velocity()
        
        # Analyze protocol dominance
        self.analyze_protocol_trends()
        
        # Analyze market cap distribution
        self.analyze_market_cap_trends()
        
        # Analyze volume patterns
        self.analyze_volume_patterns()
        
        # Generate market sentiment score
        sentiment_score = self.calculate_market_sentiment()
        
        print(f"\n🎯 OVERALL MARKET SENTIMENT: {sentiment_score}/10")
        self.interpret_sentiment(sentiment_score)
        
        # Save analysis to file
        self.save_analysis_report()
    
    def analyze_token_velocity(self):
        """Analyze how fast new tokens are being created"""
        
        if not self.market_metrics['new_tokens_per_hour']:
            return
        
        recent_hours = list(self.market_metrics['new_tokens_per_hour'])[-6:]  # Last 6 hours
        avg_tokens_per_hour = sum(hour['count'] for hour in recent_hours) / len(recent_hours)
        
        print(f"\n📈 Token Velocity Analysis:")
        print(f"   Average new tokens per hour (last 6h): {avg_tokens_per_hour:.1f}")
        
        if avg_tokens_per_hour > 50:
            print("   🔥 HIGH activity - Market is very active")
        elif avg_tokens_per_hour > 20:
            print("   📊 MEDIUM activity - Normal market conditions")
        else:
            print("   😴 LOW activity - Market is quiet")
    
    def analyze_protocol_trends(self):
        """Analyze which protocols are dominating"""
        
        print(f"\n🏗️ Protocol Distribution:")
        
        total_tokens = sum(self.market_metrics['protocol_distribution'].values())
        
        if total_tokens == 0:
            print("   No data available")
            return
        
        sorted_protocols = sorted(
            self.market_metrics['protocol_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for protocol, count in sorted_protocols[:5]:  # Top 5
            percentage = (count / total_tokens) * 100
            print(f"   {protocol}: {count} tokens ({percentage:.1f}%)")
    
    def analyze_market_cap_trends(self):
        """Analyze market cap trends"""
        
        if len(self.market_metrics['market_cap_trends']) < 10:
            return
        
        market_caps = list(self.market_metrics['market_cap_trends'])
        
        avg_market_cap = sum(market_caps) / len(market_caps)
        recent_avg = sum(market_caps[-10:]) / 10  # Last 10 tokens
        
        print(f"\n💰 Market Cap Analysis:")
        print(f"   Average market cap: {avg_market_cap:.2f} SOL")
        print(f"   Recent average (last 10): {recent_avg:.2f} SOL")
        
        if recent_avg > avg_market_cap * 1.2:
            print("   📈 Market cap trending UP - Bullish sentiment")
        elif recent_avg < avg_market_cap * 0.8:
            print("   📉 Market cap trending DOWN - Bearish sentiment")
        else:
            print("   ➡️ Market cap stable - Neutral sentiment")
    
    def analyze_volume_patterns(self):
        """Analyze volume patterns"""
        
        if len(self.market_metrics['volume_trends']) < 10:
            return
        
        volumes = list(self.market_metrics['volume_trends'])
        
        avg_volume = sum(volumes) / len(volumes)
        recent_avg = sum(volumes[-10:]) / 10
        
        print(f"\n📊 Volume Analysis:")
        print(f"   Average volume: {avg_volume:.2f} SOL")
        print(f"   Recent average (last 10): {recent_avg:.2f} SOL")
        
        if recent_avg > avg_volume * 1.3:
            print("   🚀 Volume surging - High interest")
        elif recent_avg < avg_volume * 0.7:
            print("   📉 Volume declining - Low interest")
        else:
            print("   ➡️ Volume stable - Normal interest")
    
    def calculate_market_sentiment(self):
        """Calculate overall market sentiment score (1-10)"""
        
        score = 5.0  # Neutral starting point
        
        # Factor 1: Token velocity
        if self.market_metrics['new_tokens_per_hour']:
            recent_hours = list(self.market_metrics['new_tokens_per_hour'])[-6:]
            avg_tokens = sum(hour['count'] for hour in recent_hours) / len(recent_hours)
            
            if avg_tokens > 50:
                score += 1.5  # High activity is bullish
            elif avg_tokens < 10:
                score -= 1.0  # Low activity is bearish
        
        # Factor 2: Market cap trends
        if len(self.market_metrics['market_cap_trends']) >= 20:
            market_caps = list(self.market_metrics['market_cap_trends'])
            early_avg = sum(market_caps[:10]) / 10
            recent_avg = sum(market_caps[-10:]) / 10
            
            if recent_avg > early_avg * 1.2:
                score += 1.0
            elif recent_avg < early_avg * 0.8:
                score -= 1.0
        
        # Factor 3: Volume trends
        if len(self.market_metrics['volume_trends']) >= 20:
            volumes = list(self.market_metrics['volume_trends'])
            early_avg = sum(volumes[:10]) / 10
            recent_avg = sum(volumes[-10:]) / 10
            
            if recent_avg > early_avg * 1.3:
                score += 1.0
            elif recent_avg < early_avg * 0.7:
                score -= 1.0
        
        # Factor 4: Protocol diversity
        unique_protocols = len(self.market_metrics['protocol_distribution'])
        if unique_protocols > 5:
            score += 0.5  # Diversity is good
        elif unique_protocols < 3:
            score -= 0.5  # Low diversity is concerning
        
        return max(1.0, min(10.0, score))  # Clamp between 1-10
    
    def interpret_sentiment(self, score):
        """Interpret the sentiment score"""
        
        if score >= 8:
            print("   🔥 EXTREMELY BULLISH - Great time for new investments")
        elif score >= 7:
            print("   📈 BULLISH - Positive market conditions")
        elif score >= 6:
            print("   📊 SLIGHTLY BULLISH - Cautiously optimistic")
        elif score >= 5:
            print("   ➡️ NEUTRAL - Wait for clearer signals")
        elif score >= 4:
            print("   📉 SLIGHTLY BEARISH - Exercise caution")
        elif score >= 3:
            print("   😰 BEARISH - Consider reducing exposure")
        else:
            print("   🔻 EXTREMELY BEARISH - High risk environment")
    
    def save_analysis_report(self):
        """Save analysis report to file"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'token_velocity': {
                'new_tokens_per_hour': list(self.market_metrics['new_tokens_per_hour']),
            },
            'protocol_distribution': dict(self.market_metrics['protocol_distribution']),
            'market_cap_trends': list(self.market_metrics['market_cap_trends']),
            'volume_trends': list(self.market_metrics['volume_trends']),
            'sentiment_score': self.calculate_market_sentiment()
        }
        
        with open(f"market_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Analysis report saved")
    
    async def start_analysis(self):
        """Start market sentiment analysis"""
        
        print("📊 Starting Market Sentiment Analyzer...")
        
        try:
            await self.client.subscribe_new_tokens(self.process_market_data)
            await self.client.ws.start()
        except KeyboardInterrupt:
            print("\n👋 Market analysis stopped by user")
            await self.perform_market_analysis()  # Final analysis

# Usage
async def main():
    analyzer = MarketSentimentAnalyzer(
        auth_token="your-auth-token",
        refresh_token="your-refresh-token"
    )
    
    await analyzer.start_analysis()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🛠️ WebSocket Connection Management

### Robust Connection Handling

```python
import asyncio
import logging
from axiomtradeapi import AxiomTradeClient

class RobustWebSocketClient:
    def __init__(self, auth_token, refresh_token):
        self.auth_token = auth_token
        self.refresh_token = refresh_token
        self.client = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5
        
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def connect_with_retry(self):
        """Connect with automatic retry logic"""
        
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                self.client = AxiomTradeClient(
                    auth_token=self.auth_token,
                    refresh_token=self.refresh_token
                )
                
                await self.client.subscribe_new_tokens(self.handle_tokens)
                self.logger.info("✅ WebSocket connected successfully")
                self.reconnect_attempts = 0
                return True
                
            except Exception as e:
                self.reconnect_attempts += 1
                self.logger.error(f"❌ Connection failed (attempt {self.reconnect_attempts}): {e}")
                
                if self.reconnect_attempts < self.max_reconnect_attempts:
                    await asyncio.sleep(self.reconnect_delay)
                    self.reconnect_delay *= 2  # Exponential backoff
        
        self.logger.error("🔴 Max reconnection attempts exceeded")
        return False
    
    async def handle_tokens(self, tokens):
        """Handle incoming token data"""
        for token in tokens:
            self.logger.info(f"📡 Received: {token['tokenName']}")
    
    async def start_with_monitoring(self):
        """Start with connection monitoring"""
        
        while True:
            if await self.connect_with_retry():
                try:
                    await self.client.ws.start()
                except Exception as e:
                    self.logger.error(f"❌ WebSocket error: {e}")
                    self.logger.info("🔄 Attempting to reconnect...")
                    continue
            else:
                self.logger.error("🔴 Failed to establish connection")
                break

# Usage
async def main():
    robust_client = RobustWebSocketClient(
        auth_token="your-auth-token",
        refresh_token="your-refresh-token"
    )
    
    await robust_client.start_with_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 WebSocket Performance Optimization

### High-Performance Token Processing

```python
import asyncio
import time
from collections import deque
from axiomtradeapi import AxiomTradeClient

class HighPerformanceTokenProcessor:
    def __init__(self, auth_token, refresh_token):
        self.client = AxiomTradeClient(
            auth_token=auth_token,
            refresh_token=refresh_token
        )
        
        # Performance metrics
        self.processing_times = deque(maxlen=1000)
        self.tokens_processed = 0
        self.start_time = time.time()
        
        # Async processing queue
        self.token_queue = asyncio.Queue(maxsize=10000)
        self.workers = []
    
    async def token_receiver(self, tokens):
        """Receive tokens and add to processing queue"""
        
        receive_time = time.time()
        
        for token in tokens:
            token['receive_timestamp'] = receive_time
            
            try:
                self.token_queue.put_nowait(token)
            except asyncio.QueueFull:
                print("⚠️ Warning: Token queue is full, dropping token")
    
    async def token_worker(self, worker_id):
        """Worker coroutine for processing tokens"""
        
        while True:
            try:
                # Get token from queue
                token = await self.token_queue.get()
                
                # Process token
                start_time = time.time()
                await self.process_token(token)
                end_time = time.time()
                
                # Record performance metrics
                processing_time = end_time - start_time
                self.processing_times.append(processing_time)
                self.tokens_processed += 1
                
                # Mark task as done
                self.token_queue.task_done()
                
            except Exception as e:
                print(f"❌ Worker {worker_id} error: {e}")
    
    async def process_token(self, token):
        """Process individual token (implement your logic here)"""
        
        # Simulate processing time
        await asyncio.sleep(0.01)
        
        # Your token processing logic here
        print(f"⚡ Processed: {token['tokenName']}")
    
    def get_performance_stats(self):
        """Get performance statistics"""
        
        if not self.processing_times:
            return "No performance data available"
        
        avg_processing_time = sum(self.processing_times) / len(self.processing_times)
        total_runtime = time.time() - self.start_time
        tokens_per_second = self.tokens_processed / total_runtime if total_runtime > 0 else 0
        
        return {
            'tokens_processed': self.tokens_processed,
            'avg_processing_time_ms': avg_processing_time * 1000,
            'tokens_per_second': tokens_per_second,
            'queue_size': self.token_queue.qsize(),
            'total_runtime': total_runtime
        }
    
    async def start_processing(self, num_workers=5):
        """Start high-performance token processing"""
        
        print(f"🚀 Starting high-performance processor with {num_workers} workers")
        
        # Start worker coroutines
        for i in range(num_workers):
            worker = asyncio.create_task(self.token_worker(i))
            self.workers.append(worker)
        
        # Start performance monitoring
        monitor_task = asyncio.create_task(self.performance_monitor())
        
        try:
            # Subscribe to tokens and start WebSocket
            await self.client.subscribe_new_tokens(self.token_receiver)
            await self.client.ws.start()
            
        except KeyboardInterrupt:
            print("\n👋 Stopping processor...")
            
            # Cancel workers
            for worker in self.workers:
                worker.cancel()
            
            monitor_task.cancel()
            
            # Final stats
            print("\n📊 Final Performance Stats:")
            stats = self.get_performance_stats()
            for key, value in stats.items():
                print(f"   {key}: {value}")
    
    async def performance_monitor(self):
        """Monitor and report performance every 30 seconds"""
        
        while True:
            await asyncio.sleep(30)
            
            stats = self.get_performance_stats()
            print(f"\n📊 Performance Update:")
            print(f"   Tokens processed: {stats['tokens_processed']}")
            print(f"   Processing speed: {stats['tokens_per_second']:.2f} tokens/sec")
            print(f"   Avg processing time: {stats['avg_processing_time_ms']:.2f}ms")
            print(f"   Queue size: {stats['queue_size']}")

# Usage
async def main():
    processor = HighPerformanceTokenProcessor(
        auth_token="your-auth-token",
        refresh_token="your-refresh-token"
    )
    
    await processor.start_processing(num_workers=10)

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔒 Security Best Practices

### Secure WebSocket Implementation

```python
import asyncio
import ssl
import logging
from axiomtradeapi import AxiomTradeClient

class SecureWebSocketClient:
    def __init__(self, auth_token, refresh_token):
        self.auth_token = auth_token
        self.refresh_token = refresh_token
        
        # Security configuration
        self.setup_security()
        self.setup_logging()
    
    def setup_security(self):
        """Setup security configurations"""
        
        # Create SSL context for secure connections
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = True
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # Token validation
        if not self.validate_tokens():
            raise ValueError("Invalid authentication tokens")
    
    def validate_tokens(self):
        """Validate authentication tokens"""
        
        if not self.auth_token or not self.refresh_token:
            return False
        
        # Basic JWT format validation
        if not (self.auth_token.count('.') == 2 and self.refresh_token.count('.') == 2):
            return False
        
        return True
    
    def setup_logging(self):
        """Setup security-focused logging"""
        
        # Create security logger
        self.security_logger = logging.getLogger('security')
        self.security_logger.setLevel(logging.INFO)
        
        # Security log handler
        security_handler = logging.FileHandler('security.log')
        security_formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        security_handler.setFormatter(security_formatter)
        self.security_logger.addHandler(security_handler)
    
    async def secure_token_handler(self, tokens):
        """Securely handle incoming tokens"""
        
        # Log security events
        self.security_logger.info(f"Received {len(tokens)} tokens via secure WebSocket")
        
        # Validate token data
        for token in tokens:
            if self.validate_token_data(token):
                await self.process_secure_token(token)
            else:
                self.security_logger.warning(f"Invalid token data received: {token.get('tokenAddress', 'Unknown')}")
    
    def validate_token_data(self, token):
        """Validate incoming token data"""
        
        required_fields = ['tokenName', 'tokenAddress', 'marketCapSol', 'volumeSol']
        
        for field in required_fields:
            if field not in token:
                return False
        
        # Additional validation
        if len(token['tokenAddress']) != 44:  # Solana address length
            return False
        
        if token['marketCapSol'] < 0 or token['volumeSol'] < 0:
            return False
        
        return True
    
    async def process_secure_token(self, token):
        """Process validated token data"""
        
        # Implement your secure processing logic here
        print(f"🔒 Securely processed: {token['tokenName']}")
    
    async def start_secure_connection(self):
        """Start secure WebSocket connection"""
        
        try:
            self.client = AxiomTradeClient(
                auth_token=self.auth_token,
                refresh_token=self.refresh_token
            )
            
            self.security_logger.info("Initiating secure WebSocket connection")
            
            await self.client.subscribe_new_tokens(self.secure_token_handler)
            await self.client.ws.start()
            
        except Exception as e:
            self.security_logger.error(f"Security breach or connection error: {e}")
            raise

# Usage
async def main():
    secure_client = SecureWebSocketClient(
        auth_token="your-auth-token",
        refresh_token="your-refresh-token"
    )
    
    await secure_client.start_secure_connection()

if __name__ == "__main__":
    asyncio.run(main())
```

## 🎯 Next Steps

Master WebSocket integration and ready for advanced trading?

1. **[Trading Bot Development](./trading-bots.md)** - Build automated trading strategies
2. **[Performance Optimization](./performance.md)** - Scale your real-time systems
3. **[Error Handling](./error-handling.md)** - Robust error management

## 💼 Professional WebSocket Services

Need a custom real-time trading system or advanced WebSocket integration?

[**Chipa.tech offers professional development services**](https://chipa.tech/product/create-your-bot/):
- Custom real-time trading bots
- High-frequency data processing systems
- Advanced market analysis tools
- Enterprise WebSocket solutions

[**Get Your Custom System →**](https://chipa.tech/product/create-your-bot/)

## 🛒 Explore Real-Time Tools

Visit [**Chipa.tech Shop**](https://chipa.tech/shop/) for:
- Pre-built WebSocket templates
- Real-time analysis tools
- Trading bot frameworks
- Professional monitoring solutions

---

*WebSocket integration guide by [Chipa.tech](https://chipa.tech) - Your trusted partner for real-time Solana trading automation*
