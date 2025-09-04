---
layout: api
title: "Complete API Reference - AxiomTradeAPI-py"
description: "Comprehensive API documentation for AxiomTradeAPI-py Python SDK. Complete reference for all classes, methods, and functions."
permalink: /api-reference/
---

# API Reference - AxiomTradeAPI-py

## Complete Python SDK API Documentation

This comprehensive reference covers all classes, methods, and functions available in the AxiomTradeAPI-py library. Use this as your complete guide for integrating Solana trading functionality into your applications.

---

## Core Classes

### AxiomTradeClient

The main client class for interacting with the Axiom Trade API.

```python
from axiomtradeapi import AxiomTradeClient

client = AxiomTradeClient(
    auth_token=None,
    refresh_token=None,
    log_level=logging.INFO,
    timeout=30,
    max_retries=3
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auth_token` | `str` | `None` | Authentication token for API access |
| `refresh_token` | `str` | `None` | Refresh token for token renewal |
| `log_level` | `int` | `logging.INFO` | Logging level for client operations |
| `timeout` | `int` | `30` | Request timeout in seconds |
| `max_retries` | `int` | `3` | Maximum number of retry attempts |

#### Methods

##### GetBalance(wallet_address)

Retrieve the SOL balance for a specific wallet address.

```python
balance = client.GetBalance("BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh")
```

**Parameters:**
- `wallet_address` (str): Valid Solana wallet address (44 characters)

**Returns:**
```python
{
    "sol": 1.234567890,        # Balance in SOL (float)
    "lamports": 1234567890,    # Balance in lamports (int)
    "slot": 344031778          # Blockchain slot number (int)
}
```

**Raises:**
- `ValueError`: Invalid wallet address format
- `APIError`: API request failed
- `NetworkError`: Network connectivity issues

---

##### GetBatchedBalance(wallet_addresses)

Retrieve balances for multiple wallet addresses in a single request.

```python
addresses = [
    "BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh",
    "Cpxu7gFhu3fDX1eG5ZVyiFoPmgxpLWiu5LhByNenVbPb"
]
balances = client.GetBatchedBalance(addresses)
```

**Parameters:**
- `wallet_addresses` (List[str]): List of wallet addresses (max 1000)

**Returns:**
```python
{
    "wallet_address_1": {
        "sol": 1.234567890,
        "lamports": 1234567890,
        "slot": 344031778
    },
    "wallet_address_2": {
        "sol": 0.567890123,
        "lamports": 567890123,
        "slot": 344031778
    },
    "invalid_address": None  # Failed queries return None
}
```

**Performance:**
- Supports up to 1000 addresses per request
- Average response time: < 100ms
- Automatic batching for large requests

---

##### subscribe_new_tokens(callback)

Subscribe to real-time new token launches via WebSocket.

```python
async def handle_new_tokens(tokens):
    for token in tokens:
        print(f"New token: {token['tokenName']}")

await client.subscribe_new_tokens(handle_new_tokens)
```

**Parameters:**
- `callback` (async callable): Function to handle incoming token data

**Callback Parameters:**
```python
async def callback(tokens: List[dict]):
    # tokens is a list of token objects
    pass
```

**Token Object Structure:**
```python
{
    "tokenName": "Example Token",
    "tokenTicker": "EXAMPLE",
    "tokenAddress": "token_address_here",
    "marketCapSol": 100.0,
    "volumeSol": 50.0,
    "liquiditySol": 200.0,
    "protocol": "Raydium",
    "createdAt": "2024-01-01T00:00:00Z",
    "website": "https://example.com",
    "twitter": "https://twitter.com/example",
    "telegram": "https://t.me/example"
}
```

---

## WebSocket Client

### AxiomTradeWebSocketClient

Dedicated WebSocket client for real-time data streaming.

```python
from axiomtradeapi.websocket import AxiomTradeWebSocketClient

ws_client = AxiomTradeWebSocketClient(
    auth_token="your-auth-token",
    reconnect_delay=5,
    max_reconnects=10
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auth_token` | `str` | Required | Authentication token |
| `reconnect_delay` | `int` | `5` | Delay between reconnection attempts |
| `max_reconnects` | `int` | `10` | Maximum reconnection attempts |

#### Methods

##### connect()

Establish WebSocket connection to Axiom Trade servers.

```python
await ws_client.connect()
```

**Returns:**
- `bool`: True if connection successful, False otherwise

---

##### listen()

Listen for incoming WebSocket messages.

```python
async for message in ws_client.listen():
    print(f"Received: {message}")
```

**Yields:**
- `dict`: Parsed WebSocket message data

---

##### send(message)

Send message through WebSocket connection.

```python
await ws_client.send({
    "type": "subscribe",
    "channel": "new_tokens"
})
```

**Parameters:**
- `message` (dict): Message to send

---

## Authentication

### AxiomAuth

Authentication helper class for managing API tokens.

```python
from axiomtradeapi.auth import AxiomAuth

auth = AxiomAuth()
```

#### Methods

##### login(email, password)

Authenticate with Axiom Trade using email and password.

```python
credentials = await auth.login("user@example.com", "password123")
```

**Parameters:**
- `email` (str): User email address
- `password` (str): User password

**Returns:**
```python
{
    "auth_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_at": "2024-01-01T12:00:00Z",
    "user_id": "user_123",
    "success": True
}
```

---

##### refresh_tokens(refresh_token)

Refresh authentication tokens using refresh token.

```python
new_tokens = await auth.refresh_tokens("current_refresh_token")
```

**Parameters:**
- `refresh_token` (str): Current refresh token

**Returns:**
```python
{
    "auth_token": "new_auth_token",
    "refresh_token": "new_refresh_token",
    "expires_at": "2024-01-01T13:00:00Z",
    "success": True
}
```

---

##### validate_token(auth_token)

Validate if an authentication token is still valid.

```python
is_valid = await auth.validate_token("auth_token_here")
```

**Parameters:**
- `auth_token` (str): Token to validate

**Returns:**
- `bool`: True if token is valid, False otherwise

---

## Utility Functions

### quick_login_and_get_trending()

Quick utility function to login and get trending tokens.

```python
from axiomtradeapi import quick_login_and_get_trending

trending = await quick_login_and_get_trending(
    email="user@example.com",
    password="password123"
)
```

**Parameters:**
- `email` (str): User email
- `password` (str): User password

**Returns:**
```python
{
    "trending_tokens": [
        {
            "tokenName": "Trending Token 1",
            "tokenAddress": "address1",
            "volumeSol": 1000.0,
            "priceChange24h": 15.5
        }
    ],
    "auth_token": "token_for_future_use"
}
```

---

### get_trending_with_token(auth_token)

Get trending tokens with existing authentication token.

```python
from axiomtradeapi import get_trending_with_token

trending = await get_trending_with_token("your_auth_token")
```

**Parameters:**
- `auth_token` (str): Valid authentication token

**Returns:**
- List[dict]: List of trending token objects

---

## Exception Classes

### APIError

Base exception class for API-related errors.

```python
from axiomtradeapi.exceptions import APIError

try:
    balance = client.GetBalance("invalid_address")
except APIError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Error Code: {e.error_code}")
```

**Attributes:**
- `message` (str): Human-readable error message
- `status_code` (int): HTTP status code
- `error_code` (str): Specific error identifier

---

### NetworkError

Exception raised for network connectivity issues.

```python
from axiomtradeapi.exceptions import NetworkError

try:
    balance = client.GetBalance("address")
except NetworkError as e:
    print(f"Network Error: {e.message}")
    print(f"Retry After: {e.retry_after}")
```

**Attributes:**
- `message` (str): Error description
- `retry_after` (int): Suggested retry delay in seconds

---

### AuthenticationError

Exception raised for authentication failures.

```python
from axiomtradeapi.exceptions import AuthenticationError

try:
    await client.subscribe_new_tokens(callback)
except AuthenticationError as e:
    print(f"Auth Error: {e.message}")
    print(f"Expired: {e.token_expired}")
```

**Attributes:**
- `message` (str): Error description
- `token_expired` (bool): Whether token has expired

---

### ValidationError

Exception raised for input validation errors.

```python
from axiomtradeapi.exceptions import ValidationError

try:
    balance = client.GetBalance("invalid_format")
except ValidationError as e:
    print(f"Validation Error: {e.message}")
    print(f"Field: {e.field}")
    print(f"Value: {e.value}")
```

**Attributes:**
- `message` (str): Error description
- `field` (str): Field that failed validation
- `value` (any): Invalid value provided

---

## Configuration Classes

### ClientConfig

Configuration class for customizing client behavior.

```python
from axiomtradeapi.config import ClientConfig

config = ClientConfig(
    api_base_url="https://api.axiom.trade",
    websocket_url="wss://ws.axiom.trade",
    timeout=30,
    max_retries=3,
    rate_limit={
        "requests_per_minute": 100,
        "burst_limit": 10
    }
)

client = AxiomTradeClient(config=config)
```

**Attributes:**
- `api_base_url` (str): Base URL for API requests
- `websocket_url` (str): WebSocket endpoint URL
- `timeout` (int): Request timeout in seconds
- `max_retries` (int): Maximum retry attempts
- `rate_limit` (dict): Rate limiting configuration

---

## Advanced Features

### Batch Processing

For high-volume operations, use batch processing utilities:

```python
from axiomtradeapi.batch import BatchProcessor

processor = BatchProcessor(client)

# Process 10,000 wallets efficiently
large_wallet_list = [...]  # Your wallet addresses
results = await processor.process_wallets(
    large_wallet_list,
    batch_size=100,
    concurrent_batches=5
)
```

### Connection Pooling

Optimize performance with connection pooling:

```python
from axiomtradeapi.pool import ConnectionPool

pool = ConnectionPool(
    max_connections=20,
    max_keepalive_connections=5,
    keepalive_expiry=30
)

client = AxiomTradeClient(connection_pool=pool)
```

### Retry Strategies

Customize retry behavior:

```python
from axiomtradeapi.retry import ExponentialBackoffRetry

retry_strategy = ExponentialBackoffRetry(
    max_retries=5,
    base_delay=1,
    max_delay=60,
    exponential_base=2
)

client = AxiomTradeClient(retry_strategy=retry_strategy)
```

---

## Performance Considerations

### Rate Limits

The API enforces the following rate limits:

| Endpoint | Limit | Window |
|----------|-------|--------|
| Balance queries | 100 requests | 1 minute |
| Batch operations | 10 requests | 1 minute |
| WebSocket connections | 5 connections | Per account |
| Authentication | 10 requests | 1 minute |

### Optimization Tips

1. **Use Batch Operations**: Group multiple balance queries into single requests
2. **Implement Caching**: Cache frequently accessed data to reduce API calls
3. **Connection Reuse**: Use persistent connections for better performance
4. **Async Operations**: Leverage async/await for concurrent operations

### Memory Usage

Typical memory usage patterns:

- **Basic Client**: ~10MB base memory
- **WebSocket Client**: ~15MB including buffers
- **Batch Processing**: ~1MB per 1000 addresses
- **Connection Pool**: ~5MB for 20 connections

---

## Code Examples

### Complete Trading Bot Example

```python
import asyncio
import logging
from axiomtradeapi import AxiomTradeClient

class SimpleTradingBot:
    def __init__(self, auth_token, refresh_token):
        self.client = AxiomTradeClient(
            auth_token=auth_token,
            refresh_token=refresh_token,
            log_level=logging.INFO
        )
        self.monitored_wallets = []
        
    async def start_monitoring(self):
        """Start monitoring for new tokens and portfolio changes"""
        
        # Subscribe to new tokens
        await self.client.subscribe_new_tokens(self.handle_new_token)
        
        # Start portfolio monitoring
        asyncio.create_task(self.monitor_portfolio())
        
        # Start WebSocket listener
        await self.client.ws.start()
    
    async def handle_new_token(self, tokens):
        """Handle new token announcements"""
        for token in tokens:
            if self.should_trade_token(token):
                await self.execute_trade(token)
    
    def should_trade_token(self, token):
        """Determine if we should trade this token"""
        return (
            token['marketCapSol'] > 10.0 and
            token['liquiditySol'] > 50.0 and
            token.get('verified_contract', False)
        )
    
    async def execute_trade(self, token):
        """Execute trading logic"""
        logging.info(f"Trading signal for {token['tokenName']}")
        # Implement your trading logic here
    
    async def monitor_portfolio(self):
        """Monitor portfolio performance"""
        while True:
            try:
                balances = self.client.GetBatchedBalance(self.monitored_wallets)
                total_value = sum(b['sol'] for b in balances.values() if b)
                logging.info(f"Portfolio value: {total_value:.6f} SOL")
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logging.error(f"Portfolio monitoring error: {e}")

# Usage
async def main():
    bot = SimpleTradingBot(
        auth_token="your-auth-token",
        refresh_token="your-refresh-token"
    )
    await bot.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
```

### Portfolio Analytics Example

```python
from axiomtradeapi import AxiomTradeClient
import pandas as pd
from datetime import datetime, timedelta

class PortfolioAnalyzer:
    def __init__(self, client):
        self.client = client
        self.historical_data = []
    
    def analyze_portfolio(self, wallet_addresses):
        """Perform comprehensive portfolio analysis"""
        
        # Get current balances
        balances = self.client.GetBatchedBalance(wallet_addresses)
        
        # Calculate metrics
        total_sol = sum(b['sol'] for b in balances.values() if b)
        wallet_count = len([b for b in balances.values() if b])
        avg_balance = total_sol / wallet_count if wallet_count > 0 else 0
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_value_sol': total_sol,
            'wallet_count': wallet_count,
            'average_balance': avg_balance,
            'largest_wallet': max(balances.values(), key=lambda x: x['sol'] if x else 0),
            'smallest_wallet': min(balances.values(), key=lambda x: x['sol'] if x else float('inf')),
            'distribution': self.calculate_distribution(balances)
        }
        
        return report
    
    def calculate_distribution(self, balances):
        """Calculate balance distribution statistics"""
        valid_balances = [b['sol'] for b in balances.values() if b]
        
        if not valid_balances:
            return {}
        
        df = pd.Series(valid_balances)
        
        return {
            'mean': df.mean(),
            'median': df.median(),
            'std': df.std(),
            'percentiles': {
                '25th': df.quantile(0.25),
                '75th': df.quantile(0.75),
                '90th': df.quantile(0.90),
                '95th': df.quantile(0.95)
            }
        }

# Usage
client = AxiomTradeClient()
analyzer = PortfolioAnalyzer(client)

wallets = ["wallet1", "wallet2", "wallet3"]
report = analyzer.analyze_portfolio(wallets)
print(f"Portfolio Report: {report}")
```

---

## Migration Guide

### From v0.x to v1.x

Key changes in the latest version:

1. **Client Initialization**:
   ```python
   # Old way (v0.x)
   client = AxiomTradeClient("auth_token")
   
   # New way (v1.x)
   client = AxiomTradeClient(auth_token="auth_token")
   ```

2. **WebSocket Subscription**:
   ```python
   # Old way
   client.subscribe_tokens(callback)
   
   # New way
   await client.subscribe_new_tokens(callback)
   ```

3. **Error Handling**:
   ```python
   # Old way
   try:
       balance = client.get_balance(address)
   except Exception as e:
       print(e)
   
   # New way
   try:
       balance = client.GetBalance(address)
   except APIError as e:
       print(f"API Error: {e.message}")
   except NetworkError as e:
       print(f"Network Error: {e.message}")
   ```

---

## Support and Resources

### Getting Help

- **Documentation**: [https://chipadevteam.github.io/AxiomTradeAPI-py](https://chipadevteam.github.io/AxiomTradeAPI-py)
- **Discord Community**: [https://discord.gg/p7YyFqSmAz](https://discord.gg/p7YyFqSmAz)
- **GitHub Issues**: [https://github.com/ChipaDevTeam/AxiomTradeAPI-py/issues](https://github.com/ChipaDevTeam/AxiomTradeAPI-py/issues)
- **Professional Services**: [https://shop.chipatrade.com/products/create-your-bot](https://shop.chipatrade.com/products/create-your-bot)

### Contributing

We welcome contributions! See our [Contributing Guide](https://github.com/ChipaDevTeam/AxiomTradeAPI-py/blob/main/CONTRIBUTING.md) for details.

### License

This API reference is part of the AxiomTradeAPI-py library, licensed under the MIT License.

---

*Last updated: {{ site.time | date: "%Y-%m-%d" }}*