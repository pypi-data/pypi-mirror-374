---
layout: api
title: "Balance Queries API - AxiomTradeAPI"
description: "Complete API reference for Solana wallet balance monitoring, portfolio tracking, and batch operations using AxiomTradeAPI-py."
endpoint: "/api/balance"
method: "GET"
---

# Balance Queries Guide - AxiomTradeAPI-py | Solana Wallet Monitoring SDK

## Complete Guide to Solana Wallet Balance Monitoring and Batch Operations

Master wallet balance queries with **AxiomTradeAPI-py**, the leading Python SDK for Solana balance monitoring, portfolio tracking, and automated trading bot development. This comprehensive guide covers everything from basic single wallet queries to advanced batch operations for high-frequency trading systems.

## 🚀 Quick Start: Basic Balance Queries

### Single Wallet Balance Query

Monitor any Solana wallet address in real-time:

```python
from axiomtradeapi import AxiomTradeClient

# Initialize the client
client = AxiomTradeClient()

# Query any Solana wallet balance
wallet_address = "BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh"
balance = client.GetBalance(wallet_address)

print(f"💰 Wallet Balance:")
print(f"   SOL: {balance['sol']}")
print(f"   Lamports: {balance['lamports']:,}")
print(f"   Slot: {balance['slot']}")
```

**Output:**
```
💰 Wallet Balance:
   SOL: 1.234567890
   Lamports: 1,234,567,890
   Slot: 344031778
```

## ⚡ High-Performance Batch Operations

### Monitor Multiple Wallets Simultaneously

Perfect for portfolio tracking and trading bot automation:

```python
from axiomtradeapi import AxiomTradeClient
import asyncio

# Initialize client for high-performance operations
client = AxiomTradeClient()

# Monitor multiple wallets in a single API call
wallet_addresses = [
    "BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh",
    "Cpxu7gFhu3fDX1eG5ZVyiFoPmgxpLWiu5LhByNenVbPb",
    "DsHk4F6QNTK6RdTmaDSKeFzGXMnQ9QxKTkDkG8XF8F4F",
    "8YLKwP3nQtVsF7X9mR2wCvBqA3n4H5kJ9L6mN1oP2qR3"
]

# Batch query - up to 1000 wallets per request
balances = client.GetBatchedBalance(wallet_addresses)

print("📊 Portfolio Summary:")
total_sol = 0

for address, balance_data in balances.items():
    if balance_data:
        sol_amount = balance_data['sol']
        total_sol += sol_amount
        print(f"   {address[:8]}...{address[-8:]}: {sol_amount:.6f} SOL")
    else:
        print(f"   {address[:8]}...{address[-8:]}: ❌ Error")

print(f"\n💎 Total Portfolio Value: {total_sol:.6f} SOL")
```

## 🏆 Advanced Use Cases

### 1. Portfolio Performance Tracker

Build a comprehensive portfolio monitoring system:

```python
import time
import json
from datetime import datetime
from axiomtradeapi import AxiomTradeClient

class SolanaPortfolioTracker:
    def __init__(self, wallets_file="portfolio_wallets.json"):
        self.client = AxiomTradeClient()
        self.wallets_file = wallets_file
        self.portfolio_history = []
        
        # Load wallet addresses from file
        try:
            with open(wallets_file, 'r') as f:
                self.wallet_addresses = json.load(f)
        except FileNotFoundError:
            print(f"Creating new portfolio file: {wallets_file}")
            self.wallet_addresses = []
            self.save_wallets()
    
    def add_wallet(self, address, name=None):
        """Add wallet to portfolio tracking"""
        wallet_info = {
            "address": address,
            "name": name or f"Wallet {len(self.wallet_addresses) + 1}",
            "added_date": datetime.now().isoformat()
        }
        
        self.wallet_addresses.append(wallet_info)
        self.save_wallets()
        print(f"✅ Added wallet: {wallet_info['name']}")
    
    def save_wallets(self):
        """Save wallet list to file"""
        with open(self.wallets_file, 'w') as f:
            json.dump(self.wallet_addresses, f, indent=2)
    
    def get_portfolio_snapshot(self):
        """Get current portfolio balances"""
        addresses = [w['address'] for w in self.wallet_addresses]
        
        if not addresses:
            return {"error": "No wallets in portfolio"}
        
        balances = self.client.GetBatchedBalance(addresses)
        
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "wallets": {},
            "total_sol": 0,
            "total_usd": 0  # Add price conversion later
        }
        
        for wallet_info in self.wallet_addresses:
            address = wallet_info['address']
            balance_data = balances.get(address)
            
            if balance_data:
                sol_amount = balance_data['sol']
                snapshot['wallets'][address] = {
                    "name": wallet_info['name'],
                    "sol": sol_amount,
                    "lamports": balance_data['lamports'],
                    "slot": balance_data['slot']
                }
                snapshot['total_sol'] += sol_amount
            else:
                snapshot['wallets'][address] = {
                    "name": wallet_info['name'],
                    "error": "Failed to fetch balance"
                }
        
        return snapshot
    
    def track_performance(self, duration_minutes=60):
        """Track portfolio performance over time"""
        print(f"📈 Starting portfolio tracking for {duration_minutes} minutes...")
        
        end_time = time.time() + (duration_minutes * 60)
        
        while time.time() < end_time:
            snapshot = self.get_portfolio_snapshot()
            self.portfolio_history.append(snapshot)
            
            print(f"📊 {snapshot['timestamp']}: {snapshot['total_sol']:.6f} SOL total")
            
            # Wait 1 minute between snapshots
            time.sleep(60)
        
        self.analyze_performance()
    
    def analyze_performance(self):
        """Analyze portfolio performance"""
        if len(self.portfolio_history) < 2:
            print("❌ Need at least 2 data points for analysis")
            return
        
        start_balance = self.portfolio_history[0]['total_sol']
        end_balance = self.portfolio_history[-1]['total_sol']
        change = end_balance - start_balance
        change_percent = (change / start_balance) * 100 if start_balance > 0 else 0
        
        print(f"\n📈 Portfolio Performance Analysis:")
        print(f"   Starting Balance: {start_balance:.6f} SOL")
        print(f"   Ending Balance: {end_balance:.6f} SOL")
        print(f"   Change: {change:+.6f} SOL ({change_percent:+.2f}%)")
        
        if change > 0:
            print("   📈 Portfolio increased! 🎉")
        elif change < 0:
            print("   📉 Portfolio decreased 😔")
        else:
            print("   ➡️ Portfolio unchanged")

# Usage example
tracker = SolanaPortfolioTracker()

# Add wallets to track
tracker.add_wallet("BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh", "Main Wallet")
tracker.add_wallet("Cpxu7gFhu3fDX1eG5ZVyiFoPmgxpLWiu5LhByNenVbPb", "Trading Wallet")

# Get current snapshot
snapshot = tracker.get_portfolio_snapshot()
print(json.dumps(snapshot, indent=2))

# Track performance for 1 hour
# tracker.track_performance(60)
```

### 2. Automated Balance Alerts

Set up intelligent balance monitoring with alerts:

```python
import smtplib
import asyncio
from email.mime.text import MimeText
from axiomtradeapi import AxiomTradeClient

class BalanceAlertSystem:
    def __init__(self, email_config=None):
        self.client = AxiomTradeClient()
        self.email_config = email_config
        self.alert_rules = {}
        
    def add_alert_rule(self, wallet_address, rule_type, threshold, name=None):
        """
        Add balance alert rule
        
        rule_type: 'above', 'below', 'change_percent'
        threshold: SOL amount or percentage
        """
        self.alert_rules[wallet_address] = {
            "name": name or wallet_address[:8],
            "rule_type": rule_type,
            "threshold": threshold,
            "last_balance": None
        }
        
        print(f"✅ Added alert rule: {name} - {rule_type} {threshold}")
    
    def check_alerts(self):
        """Check all alert rules and trigger notifications"""
        addresses = list(self.alert_rules.keys())
        
        if not addresses:
            return
        
        balances = self.client.GetBatchedBalance(addresses)
        
        for address, balance_data in balances.items():
            if not balance_data:
                continue
                
            rule = self.alert_rules[address]
            current_balance = balance_data['sol']
            
            alert_triggered = False
            alert_message = ""
            
            if rule['rule_type'] == 'above' and current_balance > rule['threshold']:
                alert_triggered = True
                alert_message = f"Balance above {rule['threshold']} SOL: {current_balance}"
                
            elif rule['rule_type'] == 'below' and current_balance < rule['threshold']:
                alert_triggered = True
                alert_message = f"Balance below {rule['threshold']} SOL: {current_balance}"
                
            elif rule['rule_type'] == 'change_percent' and rule['last_balance']:
                change_percent = ((current_balance - rule['last_balance']) / rule['last_balance']) * 100
                if abs(change_percent) > rule['threshold']:
                    alert_triggered = True
                    alert_message = f"Balance changed by {change_percent:+.2f}%: {current_balance} SOL"
            
            if alert_triggered:
                self.send_alert(rule['name'], alert_message, address)
            
            # Update last balance
            rule['last_balance'] = current_balance
    
    def send_alert(self, wallet_name, message, address):
        """Send alert notification"""
        alert_text = f"🚨 WALLET ALERT: {wallet_name}\n{message}\nAddress: {address}"
        
        print(alert_text)
        
        # Send email if configured
        if self.email_config:
            self.send_email_alert(wallet_name, alert_text)
        
        # Add Discord/Telegram/Slack notifications here
    
    def send_email_alert(self, subject, message):
        """Send email alert"""
        try:
            msg = MimeText(message)
            msg['Subject'] = f"Solana Balance Alert: {subject}"
            msg['From'] = self.email_config['from']
            msg['To'] = self.email_config['to']
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            print("📧 Email alert sent successfully")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
    
    async def monitor_continuously(self, check_interval=300):
        """Continuously monitor wallets for alerts"""
        print(f"🔍 Starting continuous monitoring (checking every {check_interval} seconds)")
        
        while True:
            try:
                self.check_alerts()
                await asyncio.sleep(check_interval)
            except KeyboardInterrupt:
                print("\n👋 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error during monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

# Usage example
email_config = {
    'smtp_server': 'smtp.gmail.com',
    'port': 587,
    'username': 'your-email@gmail.com',
    'password': 'your-app-password',
    'from': 'your-email@gmail.com',
    'to': 'alerts@your-domain.com'
}

alert_system = BalanceAlertSystem(email_config)

# Add alert rules
alert_system.add_alert_rule(
    "BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh",
    "below",
    1.0,  # Alert if balance goes below 1 SOL
    "Main Wallet"
)

alert_system.add_alert_rule(
    "Cpxu7gFhu3fDX1eG5ZVyiFoPmgxpLWiu5LhByNenVbPb",
    "change_percent",
    10.0,  # Alert if balance changes by more than 10%
    "Trading Wallet"
)

# Start monitoring
# asyncio.run(alert_system.monitor_continuously(300))  # Check every 5 minutes
```

### 3. DeFi Yield Farming Monitor

Track DeFi positions and yields across multiple protocols:

```python
from axiomtradeapi import AxiomTradeClient
import json
from datetime import datetime, timedelta

class DeFiYieldTracker:
    def __init__(self):
        self.client = AxiomTradeClient()
        self.defi_positions = {}
        self.yield_history = []
    
    def add_defi_position(self, wallet_address, protocol, position_type, initial_amount):
        """Add DeFi position for tracking"""
        position_id = f"{protocol}_{wallet_address[:8]}"
        
        self.defi_positions[position_id] = {
            "wallet_address": wallet_address,
            "protocol": protocol,
            "position_type": position_type,
            "initial_amount": initial_amount,
            "start_date": datetime.now().isoformat(),
            "history": []
        }
        
        print(f"✅ Added DeFi position: {protocol} - {position_type}")
    
    def calculate_yields(self):
        """Calculate current yields for all positions"""
        addresses = [pos['wallet_address'] for pos in self.defi_positions.values()]
        
        if not addresses:
            return {}
        
        balances = self.client.GetBatchedBalance(addresses)
        yields = {}
        
        for position_id, position in self.defi_positions.items():
            address = position['wallet_address']
            balance_data = balances.get(address)
            
            if not balance_data:
                continue
            
            current_amount = balance_data['sol']
            initial_amount = position['initial_amount']
            
            # Calculate yield
            absolute_yield = current_amount - initial_amount
            yield_percent = (absolute_yield / initial_amount) * 100 if initial_amount > 0 else 0
            
            # Calculate APY (annualized)
            start_date = datetime.fromisoformat(position['start_date'])
            days_elapsed = (datetime.now() - start_date).days
            
            if days_elapsed > 0:
                daily_yield = yield_percent / days_elapsed
                apy = ((1 + daily_yield/100) ** 365 - 1) * 100
            else:
                apy = 0
            
            yields[position_id] = {
                "protocol": position['protocol'],
                "position_type": position['position_type'],
                "initial_amount": initial_amount,
                "current_amount": current_amount,
                "absolute_yield": absolute_yield,
                "yield_percent": yield_percent,
                "apy": apy,
                "days_elapsed": days_elapsed
            }
        
        return yields
    
    def generate_yield_report(self):
        """Generate comprehensive yield farming report"""
        yields = self.calculate_yields()
        
        if not yields:
            return "No DeFi positions to report"
        
        report = "\n🌾 DeFi Yield Farming Report\n"
        report += "=" * 50 + "\n"
        
        total_initial = 0
        total_current = 0
        
        for position_id, yield_data in yields.items():
            total_initial += yield_data['initial_amount']
            total_current += yield_data['current_amount']
            
            report += f"\n📊 {yield_data['protocol']} - {yield_data['position_type']}\n"
            report += f"   Initial: {yield_data['initial_amount']:.6f} SOL\n"
            report += f"   Current: {yield_data['current_amount']:.6f} SOL\n"
            report += f"   Yield: {yield_data['absolute_yield']:+.6f} SOL ({yield_data['yield_percent']:+.2f}%)\n"
            report += f"   APY: {yield_data['apy']:.2f}%\n"
            report += f"   Duration: {yield_data['days_elapsed']} days\n"
        
        # Portfolio summary
        total_yield = total_current - total_initial
        total_yield_percent = (total_yield / total_initial) * 100 if total_initial > 0 else 0
        
        report += f"\n💎 Portfolio Summary:\n"
        report += f"   Total Initial: {total_initial:.6f} SOL\n"
        report += f"   Total Current: {total_current:.6f} SOL\n"
        report += f"   Total Yield: {total_yield:+.6f} SOL ({total_yield_percent:+.2f}%)\n"
        
        return report

# Usage example
yield_tracker = DeFiYieldTracker()

# Add DeFi positions
yield_tracker.add_defi_position(
    "BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh",
    "Raydium",
    "SOL-USDC LP",
    10.0
)

yield_tracker.add_defi_position(
    "Cpxu7gFhu3fDX1eG5ZVyiFoPmgxpLWiu5LhByNenVbPb",
    "Orca",
    "SOL-mSOL LP",
    5.0
)

# Generate yield report
report = yield_tracker.generate_yield_report()
print(report)
```

## 🚀 Performance Optimization Tips

### 1. Efficient Batch Processing

```python
from axiomtradeapi import AxiomTradeClient
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OptimizedBalanceChecker:
    def __init__(self, max_workers=5):
        self.client = AxiomTradeClient()
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def process_large_wallet_list(self, wallet_addresses, batch_size=100):
        """Process thousands of wallets efficiently"""
        
        # Split into batches
        batches = [
            wallet_addresses[i:i + batch_size]
            for i in range(0, len(wallet_addresses), batch_size)
        ]
        
        print(f"📊 Processing {len(wallet_addresses)} wallets in {len(batches)} batches")
        
        all_balances = {}
        
        for i, batch in enumerate(batches):
            print(f"⏳ Processing batch {i+1}/{len(batches)}")
            
            batch_balances = self.client.GetBatchedBalance(batch)
            all_balances.update(batch_balances)
            
            # Small delay to respect rate limits
            if i < len(batches) - 1:
                time.sleep(0.1)
        
        return all_balances

# Process 1000+ wallets efficiently
optimizer = OptimizedBalanceChecker()
large_wallet_list = ["wallet1...", "wallet2...", ...]  # Your wallet list
balances = optimizer.process_large_wallet_list(large_wallet_list)
```

### 2. Caching for Repeated Queries

```python
import time
from functools import lru_cache
from axiomtradeapi import AxiomTradeClient

class CachedBalanceClient:
    def __init__(self, cache_duration=60):
        self.client = AxiomTradeClient()
        self.cache = {}
        self.cache_duration = cache_duration
    
    def get_balance_cached(self, wallet_address):
        """Get balance with caching to reduce API calls"""
        
        current_time = time.time()
        cache_key = wallet_address
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            
            if current_time - timestamp < self.cache_duration:
                print(f"📋 Using cached data for {wallet_address[:8]}...")
                return cached_data
        
        # Fetch fresh data
        print(f"🔄 Fetching fresh data for {wallet_address[:8]}...")
        balance = self.client.GetBalance(wallet_address)
        
        # Cache the result
        self.cache[cache_key] = (balance, current_time)
        
        return balance
    
    def clear_cache(self):
        """Clear the balance cache"""
        self.cache.clear()
        print("🗑️ Cache cleared")

# Usage
cached_client = CachedBalanceClient(cache_duration=120)  # 2-minute cache

# First call fetches from API
balance1 = cached_client.get_balance_cached("BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh")

# Second call uses cache
balance2 = cached_client.get_balance_cached("BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh")
```

## 📊 Response Data Structure

Understanding the complete response format:

```python
# Single balance response
{
    "sol": 1.234567890,        # Balance in SOL (float)
    "lamports": 1234567890,    # Balance in lamports (int)
    "slot": 344031778          # Blockchain slot number (int)
}

# Batch balance response
{
    "BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh": {
        "sol": 1.234567890,
        "lamports": 1234567890,
        "slot": 344031778
    },
    "Cpxu7gFhu3fDX1eG5ZVyiFoPmgxpLWiu5LhByNenVbPb": {
        "sol": 0.567890123,
        "lamports": 567890123,
        "slot": 344031778
    },
    "InvalidWalletAddress...": None  # Failed queries return None
}
```

## 🚨 Error Handling Best Practices

```python
from axiomtradeapi import AxiomTradeClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def robust_balance_query(client, wallet_address, max_retries=3):
    """Robust balance query with retry logic"""
    
    for attempt in range(max_retries):
        try:
            balance = client.GetBalance(wallet_address)
            
            if balance and 'sol' in balance:
                return balance
            else:
                logger.warning(f"Invalid balance data for {wallet_address}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error (attempt {attempt + 1}): {e}")
            
        except Exception as e:
            logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
        
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    logger.error(f"Failed to get balance after {max_retries} attempts")
    return None

# Usage
client = AxiomTradeClient()
balance = robust_balance_query(client, "BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh")

if balance:
    print(f"✅ Balance: {balance['sol']} SOL")
else:
    print("❌ Failed to retrieve balance")
```

## 🎯 Next Steps

Master balance queries and ready for more advanced features?

1. **[WebSocket Integration](./websocket-guide.md)** - Real-time balance monitoring
2. **[Trading Bot Development](./trading-bots.md)** - Automated trading strategies
3. **[Performance Optimization](./performance.md)** - Scale your monitoring system

## 💼 Professional Portfolio Services

Need a custom portfolio monitoring solution or advanced trading system?

[**Chipa.tech offers professional development services**](https://chipa.tech/product/create-your-bot/):
- Custom portfolio trackers
- Advanced analytics dashboards
- Multi-exchange integration
- Real-time alerting systems

[**Get Your Custom Solution →**](https://chipa.tech/product/create-your-bot/)

## 🛒 Explore Our Tools

Visit [**Chipa.tech Shop**](https://chipa.tech/shop/) for:
- Pre-built portfolio trackers
- Advanced monitoring tools
- Trading bot templates
- Professional support packages

---

*Balance queries guide by [Chipa.tech](https://chipa.tech) - Your trusted partner for Solana wallet monitoring and trading automation*
