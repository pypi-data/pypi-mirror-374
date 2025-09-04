---
layout: page
title: "Authentication Guide - Secure API Setup"
description: "Complete authentication setup guide for AxiomTradeAPI-py. Learn how to securely authenticate with Axiom Trade API for professional trading bot development."
---

# Authentication Guide - AxiomTradeAPI-py | Secure Solana Trading Bot Setup

## Complete Authentication Setup for Axiom Trade API Integration

Secure authentication is crucial for professional Solana trading bots and DeFi automation systems. This comprehensive guide covers everything you need to know about authenticating with the Axiom Trade API using our Python SDK.

## 🔐 Authentication Overview

AxiomTradeAPI-py supports multiple authentication methods:

1. **Public Access** - For basic balance queries and market data
2. **Authenticated Access** - For WebSocket subscriptions and advanced features
3. **Production Authentication** - Enterprise-grade security for trading bots

## 🚀 Quick Authentication Setup

### Basic Authentication (5 minutes)

For WebSocket features and real-time token monitoring:

```python
from axiomtradeapi import AxiomTradeClient
import os

# Store your tokens securely
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
REFRESH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Initialize authenticated client
client = AxiomTradeClient(
    auth_token=AUTH_TOKEN,
    refresh_token=REFRESH_TOKEN
)

print("🔐 Authenticated client ready for advanced trading features!")
```

## 🔑 Obtaining Authentication Tokens

### Method 1: Browser Developer Tools (Quickest)

1. **Visit Axiom Trade**: Navigate to [https://axiom.trade](https://axiom.trade)
2. **Login to Your Account**: Sign in with your credentials
3. **Open Developer Tools**: Press `F12` or right-click → "Inspect"
4. **Go to Application Tab**: Navigate to Application → Storage → Cookies
5. **Find Your Tokens**:
   - Look for `auth-access-token`
   - Look for `auth-refresh-token`
6. **Copy the Values**: These are your authentication tokens

### Method 2: Network Tab Method

1. **Open Network Tab**: In developer tools, go to Network tab
2. **Make an API Request**: Perform any action on Axiom Trade
3. **Check Request Headers**: Look for requests to `axiom.trade/api`
4. **Copy Cookie Header**: Extract tokens from the Cookie header

### Method 3: Programmatic Login (Advanced)

```python
import requests
import json

def login_to_axiom(username, password):
    """
    Programmatic login to Axiom Trade
    Returns authentication tokens for bot usage
    """
    
    login_url = "https://axiom.trade/api/auth/login"
    
    payload = {
        "email": username,
        "password": password
    }
    
    headers = {
        "Content-Type": "application/json",
        "Origin": "https://axiom.trade"
    }
    
    try:
        response = requests.post(login_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            # Extract tokens from response cookies
            auth_token = response.cookies.get('auth-access-token')
            refresh_token = response.cookies.get('auth-refresh-token')
            
            return {
                "auth_token": auth_token,
                "refresh_token": refresh_token,
                "success": True
            }
        else:
            return {"success": False, "error": response.text}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# Usage
credentials = login_to_axiom("your-email@example.com", "your-password")
if credentials["success"]:
    print("✅ Login successful!")
    print(f"Auth Token: {credentials['auth_token'][:20]}...")
else:
    print(f"❌ Login failed: {credentials['error']}")
```

## 🛡️ Secure Token Management

### Environment Variables (Recommended)

Never hardcode tokens in your source code:

```bash
# .env file (never commit this to git!)
AXIOM_AUTH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
AXIOM_REFRESH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

```python
# secure_trading_bot.py
import os
from dotenv import load_dotenv
from axiomtradeapi import AxiomTradeClient

# Load environment variables
load_dotenv()

# Secure authentication
client = AxiomTradeClient(
    auth_token=os.getenv('AXIOM_AUTH_TOKEN'),
    refresh_token=os.getenv('AXIOM_REFRESH_TOKEN')
)

print("🔒 Securely authenticated trading bot ready!")
```

### Production Secrets Management

For enterprise trading systems:

```python
# Using AWS Secrets Manager
import boto3
import json

def get_axiom_credentials():
    """Retrieve credentials from AWS Secrets Manager"""
    
    client = boto3.client('secretsmanager', region_name='us-east-1')
    
    try:
        response = client.get_secret_value(SecretId='axiom-trade-credentials')
        credentials = json.loads(response['SecretString'])
        
        return {
            'auth_token': credentials['auth_token'],
            'refresh_token': credentials['refresh_token']
        }
    except Exception as e:
        print(f"Failed to retrieve credentials: {e}")
        return None

# Initialize with secure credentials
creds = get_axiom_credentials()
if creds:
    client = AxiomTradeClient(
        auth_token=creds['auth_token'],
        refresh_token=creds['refresh_token']
    )
```

### Azure Key Vault Integration

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def get_credentials_from_keyvault():
    """Retrieve Axiom Trade credentials from Azure Key Vault"""
    
    credential = DefaultAzureCredential()
    client = SecretClient(
        vault_url="https://your-keyvault.vault.azure.net/",
        credential=credential
    )
    
    auth_token = client.get_secret("axiom-auth-token").value
    refresh_token = client.get_secret("axiom-refresh-token").value
    
    return auth_token, refresh_token

# Secure initialization
auth_token, refresh_token = get_credentials_from_keyvault()
client = AxiomTradeClient(
    auth_token=auth_token,
    refresh_token=refresh_token
)
```

## 🔄 Token Refresh and Management

### Automatic Token Refresh

```python
import time
import requests
from axiomtradeapi import AxiomTradeClient

class SecureAxiomClient:
    def __init__(self, auth_token, refresh_token):
        self.auth_token = auth_token
        self.refresh_token = refresh_token
        self.client = None
        self.token_expiry = time.time() + 3600  # 1 hour default
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the client with current tokens"""
        self.client = AxiomTradeClient(
            auth_token=self.auth_token,
            refresh_token=self.refresh_token
        )
    
    def _refresh_tokens(self):
        """Refresh authentication tokens"""
        
        refresh_url = "https://axiom.trade/api/auth/refresh"
        headers = {
            "Cookie": f"auth-refresh-token={self.refresh_token}"
        }
        
        try:
            response = requests.post(refresh_url, headers=headers)
            
            if response.status_code == 200:
                self.auth_token = response.cookies.get('auth-access-token')
                new_refresh = response.cookies.get('auth-refresh-token')
                
                if new_refresh:
                    self.refresh_token = new_refresh
                
                self.token_expiry = time.time() + 3600
                self._initialize_client()
                
                print("✅ Tokens refreshed successfully")
                return True
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Token refresh error: {e}")
            return False
    
    def ensure_valid_tokens(self):
        """Ensure tokens are valid before API calls"""
        if time.time() >= self.token_expiry - 300:  # Refresh 5 minutes early
            return self._refresh_tokens()
        return True
    
    def get_balance(self, wallet_address):
        """Get balance with automatic token refresh"""
        if not self.ensure_valid_tokens():
            raise Exception("Failed to refresh authentication tokens")
        
        return self.client.GetBalance(wallet_address)

# Usage
secure_client = SecureAxiomClient(
    auth_token="your-auth-token",
    refresh_token="your-refresh-token"
)

# Automatic token management
balance = secure_client.get_balance("BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh")
print(f"Balance: {balance['sol']} SOL")
```

## 🧪 Testing Authentication

### Authentication Validation Script

```python
import asyncio
from axiomtradeapi import AxiomTradeClient

async def test_authentication(auth_token, refresh_token):
    """Comprehensive authentication testing"""
    
    print("🔍 Testing Axiom Trade Authentication...")
    print("=" * 50)
    
    # Test 1: Basic authentication
    try:
        client = AxiomTradeClient(
            auth_token=auth_token,
            refresh_token=refresh_token
        )
        print("✅ Authentication initialization: PASSED")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False
    
    # Test 2: Authenticated API call
    try:
        balance = client.GetBalance("BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh")
        print(f"✅ Authenticated API call: PASSED - {balance['sol']} SOL")
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False
    
    # Test 3: WebSocket authentication
    try:
        async def dummy_callback(tokens):
            print(f"📡 Received {len(tokens)} token updates")
        
        await client.subscribe_new_tokens(dummy_callback)
        print("✅ WebSocket authentication: PASSED")
    except Exception as e:
        print(f"❌ WebSocket authentication failed: {e}")
        return False
    
    print("\n🎉 All authentication tests passed!")
    print("🚀 Ready for advanced Solana trading features!")
    
    return True

# Run authentication tests
async def main():
    AUTH_TOKEN = "your-auth-token-here"
    REFRESH_TOKEN = "your-refresh-token-here"
    
    await test_authentication(AUTH_TOKEN, REFRESH_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
```

## 🚨 Security Best Practices

### 1. Token Storage Security

```python
# ❌ NEVER do this - tokens exposed in code
client = AxiomTradeClient(
    auth_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  # BAD!
    refresh_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."   # BAD!
)

# ✅ DO this - secure environment variables
import os
client = AxiomTradeClient(
    auth_token=os.getenv('AXIOM_AUTH_TOKEN'),
    refresh_token=os.getenv('AXIOM_REFRESH_TOKEN')
)
```

### 2. Token Rotation Strategy

```python
import schedule
import time

class TokenManager:
    def __init__(self):
        self.client = None
        self.setup_auto_refresh()
    
    def refresh_tokens_daily(self):
        """Refresh tokens daily for security"""
        print("🔄 Performing daily token refresh...")
        # Implement token refresh logic
        
    def setup_auto_refresh(self):
        """Setup automatic token refresh schedule"""
        schedule.every(12).hours.do(self.refresh_tokens_daily)
        
        # Run scheduler in background
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        import threading
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
```

### 3. Rate Limiting and Monitoring

```python
import time
import logging
from collections import deque

class RateLimitedAxiomClient:
    def __init__(self, auth_token, refresh_token, max_requests_per_minute=60):
        self.client = AxiomTradeClient(auth_token, refresh_token)
        self.request_times = deque()
        self.max_requests = max_requests_per_minute
        
        # Setup monitoring
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _check_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        now = time.time()
        
        # Remove requests older than 1 minute
        while self.request_times and self.request_times[0] < now - 60:
            self.request_times.popleft()
        
        if len(self.request_times) >= self.max_requests:
            wait_time = 60 - (now - self.request_times[0])
            self.logger.warning(f"Rate limit reached. Waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
        
        self.request_times.append(now)
    
    def get_balance(self, wallet_address):
        """Rate-limited balance query"""
        self._check_rate_limit()
        return self.client.GetBalance(wallet_address)
```

## 🔗 Integration Examples

### Discord Bot Integration

```python
import discord
from discord.ext import commands
from axiomtradeapi import AxiomTradeClient

class SolanaBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.axiom_client = AxiomTradeClient(
            auth_token=os.getenv('AXIOM_AUTH_TOKEN'),
            refresh_token=os.getenv('AXIOM_REFRESH_TOKEN')
        )
    
    @commands.command(name='balance')
    async def check_balance(self, ctx, wallet_address):
        """Check Solana wallet balance"""
        try:
            balance = self.axiom_client.GetBalance(wallet_address)
            await ctx.send(f"💰 Balance: {balance['sol']} SOL")
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

# Discord bot setup
bot = commands.Bot(command_prefix='!')
bot.add_cog(SolanaBot(bot))
bot.run(os.getenv('DISCORD_TOKEN'))
```

### Telegram Bot Integration

```python
import telegram
from telegram.ext import Updater, CommandHandler
from axiomtradeapi import AxiomTradeClient

# Initialize Axiom client
axiom_client = AxiomTradeClient(
    auth_token=os.getenv('AXIOM_AUTH_TOKEN'),
    refresh_token=os.getenv('AXIOM_REFRESH_TOKEN')
)

def balance_command(update, context):
    """Telegram command to check wallet balance"""
    if not context.args:
        update.message.reply_text("Please provide a wallet address!")
        return
    
    wallet_address = context.args[0]
    
    try:
        balance = axiom_client.GetBalance(wallet_address)
        update.message.reply_text(f"💰 Balance: {balance['sol']} SOL")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {e}")

# Setup Telegram bot
updater = Updater(token=os.getenv('TELEGRAM_TOKEN'))
updater.dispatcher.add_handler(CommandHandler('balance', balance_command))
updater.start_polling()
```

## 📊 Authentication Performance Metrics

Monitor your authentication performance:

```python
import time
import statistics

class AuthMetrics:
    def __init__(self):
        self.response_times = []
        self.success_count = 0
        self.failure_count = 0
    
    def record_request(self, start_time, success=True):
        """Record authentication request metrics"""
        response_time = time.time() - start_time
        self.response_times.append(response_time)
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
    
    def get_stats(self):
        """Get authentication performance statistics"""
        if not self.response_times:
            return "No data available"
        
        return {
            "avg_response_time": statistics.mean(self.response_times),
            "success_rate": self.success_count / (self.success_count + self.failure_count),
            "total_requests": len(self.response_times)
        }

# Usage
metrics = AuthMetrics()

start = time.time()
try:
    balance = client.GetBalance(wallet_address)
    metrics.record_request(start, success=True)
except:
    metrics.record_request(start, success=False)

print(metrics.get_stats())
```

## 🎯 Next Steps

Now that you have secure authentication set up:

1. **[WebSocket Integration](./websocket-guide.md)** - Real-time token monitoring
2. **[Build Trading Bots](./trading-bots.md)** - Automated trading strategies
3. **[Performance Optimization](./performance.md)** - Scale your trading system

## 💼 Professional Development Services

Need help with complex authentication scenarios or enterprise security?

[**Chipa.tech offers professional services**](https://chipa.tech/product/create-your-bot/):
- Custom authentication solutions
- Enterprise security implementations
- Multi-exchange integration
- 24/7 monitoring and support

[**Get Expert Help →**](https://chipa.tech/product/create-your-bot/)

## 🛒 Explore Our Security Tools

Visit [**Chipa.tech Shop**](https://chipa.tech/shop/) for:
- Advanced authentication modules
- Security monitoring tools
- Enterprise trading solutions
- Professional support packages

---

*Authentication guide by [Chipa.tech](https://chipa.tech) - Your trusted partner for secure Solana trading automation*
