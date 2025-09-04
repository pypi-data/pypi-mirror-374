---
layout: guide
title: "Troubleshooting Guide - AxiomTradeAPI-py"
description: "Complete troubleshooting guide for AxiomTradeAPI-py. Solutions for common issues, error messages, and debugging tips."
permalink: /troubleshooting/
---

# Troubleshooting Guide - AxiomTradeAPI-py

## Complete Problem-Solving Guide for Common Issues

Having issues with AxiomTradeAPI-py? This comprehensive troubleshooting guide covers the most common problems and their solutions. Use the quick navigation below to jump to your specific issue.

---

## 🔍 Quick Issue Navigator

| Issue Category | Common Problems |
|----------------|-----------------|
| [🛠️ Installation](#installation-issues) | Package not found, dependency conflicts |
| [🔐 Authentication](#authentication-issues) | Token errors, permission denied |
| [🌐 Network & API](#network--api-issues) | Connection timeouts, rate limits |
| [📡 WebSocket](#websocket-issues) | Connection drops, subscription failures |
| [⚡ Performance](#performance-issues) | Slow responses, memory usage |
| [🐛 Common Errors](#common-error-messages) | Specific error message solutions |

---

## 🛠️ Installation Issues

### Problem: "No module named 'axiomtradeapi'"

**Symptoms:**
```python
ImportError: No module named 'axiomtradeapi'
ModuleNotFoundError: No module named 'axiomtradeapi'
```

**Solutions:**

1. **Verify Installation:**
   ```bash
   pip list | grep axiomtradeapi
   ```

2. **Install/Reinstall:**
   ```bash
   pip install axiomtradeapi
   # Or force reinstall
   pip install --force-reinstall axiomtradeapi
   ```

3. **Check Virtual Environment:**
   ```bash
   # Ensure you're in the right environment
   which python
   which pip
   
   # Activate your environment if needed
   source your-env/bin/activate  # Linux/Mac
   your-env\Scripts\activate     # Windows
   ```

4. **Python Version Check:**
   ```bash
   python --version  # Must be 3.8+
   ```

### Problem: Dependency Conflicts

**Symptoms:**
```
ERROR: pip's dependency resolver does not currently consider all the packages that are installed
```

**Solutions:**

1. **Clean Installation:**
   ```bash
   pip uninstall axiomtradeapi
   pip cache purge
   pip install axiomtradeapi
   ```

2. **Use Virtual Environment:**
   ```bash
   python -m venv clean-env
   source clean-env/bin/activate
   pip install axiomtradeapi
   ```

3. **Manual Dependency Installation:**
   ```bash
   pip install requests>=2.25.0
   pip install websockets>=10.0
   pip install axiomtradeapi
   ```

### Problem: Permission Errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **User Installation:**
   ```bash
   pip install --user axiomtradeapi
   ```

2. **Virtual Environment (Recommended):**
   ```bash
   python -m venv trading-env
   source trading-env/bin/activate
   pip install axiomtradeapi
   ```

3. **Check Directory Permissions:**
   ```bash
   ls -la $(python -m site --user-site)
   ```

---

## 🔐 Authentication Issues

### Problem: "Authentication failed" or "Invalid token"

**Symptoms:**
```python
AuthenticationError: Invalid authentication token
HTTP 401: Unauthorized
```

**Diagnostic Steps:**

1. **Check Token Format:**
   ```python
   from config import Config
   
   print(f"Auth token length: {len(Config.AUTH_TOKEN) if Config.AUTH_TOKEN else 0}")
   print(f"Token starts with 'eyJ': {Config.AUTH_TOKEN.startswith('eyJ') if Config.AUTH_TOKEN else False}")
   ```

2. **Verify Token Validity:**
   ```python
   import base64
   import json
   
   def decode_jwt_payload(token):
       try:
           # JWT tokens have 3 parts separated by '.'
           parts = token.split('.')
           if len(parts) != 3:
               return "Invalid JWT format"
           
           # Decode payload (second part)
           payload = parts[1]
           # Add padding if needed
           payload += '=' * (4 - len(payload) % 4)
           decoded = base64.b64decode(payload)
           return json.loads(decoded)
       except Exception as e:
           return f"Error decoding: {e}"
   
   # Check your token
   if Config.AUTH_TOKEN:
       payload = decode_jwt_payload(Config.AUTH_TOKEN)
       print(f"Token payload: {payload}")
   ```

**Solutions:**

1. **Refresh Your Tokens:**
   ```python
   from axiomtradeapi.auth import AxiomAuth
   
   auth = AxiomAuth()
   new_tokens = await auth.refresh_tokens(Config.REFRESH_TOKEN)
   ```

2. **Re-obtain Tokens from Browser:**
   - Visit [Axiom Trade](https://axiom.trade)
   - Login to your account
   - Open Developer Tools (F12)
   - Go to Application → Cookies
   - Find `auth-access-token` and `auth-refresh-token`
   - Update your `.env` file

3. **Check Environment Variables:**
   ```bash
   # Linux/Mac
   echo $AXIOM_AUTH_TOKEN
   
   # Windows
   echo %AXIOM_AUTH_TOKEN%
   ```

### Problem: Token Expiration

**Symptoms:**
```
Token has expired
HTTP 401 after working previously
```

**Solutions:**

1. **Automatic Token Refresh:**
   ```python
   class AutoRefreshClient:
       def __init__(self, auth_token, refresh_token):
           self.auth_token = auth_token
           self.refresh_token = refresh_token
           self.client = None
           self.token_expires_at = None
       
       async def get_client(self):
           if self.token_expires_at and time.time() > self.token_expires_at:
               await self.refresh_tokens()
           
           if not self.client:
               self.client = AxiomTradeClient(
                   auth_token=self.auth_token,
                   refresh_token=self.refresh_token
               )
           return self.client
   ```

2. **Manual Token Refresh:**
   ```python
   from axiomtradeapi.auth import AxiomAuth
   
   auth = AxiomAuth()
   result = await auth.refresh_tokens(refresh_token)
   
   if result['success']:
       # Update your tokens
       new_auth_token = result['auth_token']
       new_refresh_token = result['refresh_token']
   ```

---

## 🌐 Network & API Issues

### Problem: Connection Timeouts

**Symptoms:**
```python
requests.exceptions.ConnectTimeout
requests.exceptions.ReadTimeout
```

**Diagnostic Commands:**

```bash
# Test basic connectivity
ping axiom.trade

# Test HTTPS connection
curl -I https://axiom.trade

# Check DNS resolution
nslookup axiom.trade
```

**Solutions:**

1. **Increase Timeout:**
   ```python
   client = AxiomTradeClient(timeout=60)  # 60 seconds
   ```

2. **Retry Logic:**
   ```python
   import time
   
   def with_retry(func, max_retries=3, delay=2):
       for attempt in range(max_retries):
           try:
               return func()
           except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
               if attempt == max_retries - 1:
                   raise e
               time.sleep(delay * (2 ** attempt))  # Exponential backoff
   
   # Usage
   balance = with_retry(lambda: client.GetBalance(wallet_address))
   ```

3. **Check Proxy Settings:**
   ```python
   import os
   print("HTTP_PROXY:", os.environ.get('HTTP_PROXY'))
   print("HTTPS_PROXY:", os.environ.get('HTTPS_PROXY'))
   ```

### Problem: Rate Limiting

**Symptoms:**
```
HTTP 429: Too Many Requests
Rate limit exceeded
```

**Solutions:**

1. **Implement Rate Limiting:**
   ```python
   import time
   from collections import deque
   
   class RateLimiter:
       def __init__(self, max_requests=100, time_window=60):
           self.max_requests = max_requests
           self.time_window = time_window
           self.requests = deque()
       
       def wait_if_needed(self):
           now = time.time()
           
           # Remove old requests
           while self.requests and self.requests[0] < now - self.time_window:
               self.requests.popleft()
           
           # Check if we need to wait
           if len(self.requests) >= self.max_requests:
               wait_time = self.time_window - (now - self.requests[0])
               if wait_time > 0:
                   time.sleep(wait_time)
           
           self.requests.append(now)
   
   # Usage
   rate_limiter = RateLimiter(max_requests=50, time_window=60)
   
   def safe_api_call(func):
       rate_limiter.wait_if_needed()
       return func()
   ```

2. **Batch Operations:**
   ```python
   # Instead of multiple single calls
   for wallet in wallets:
       balance = client.GetBalance(wallet)  # Many API calls
   
   # Use batch operation
   balances = client.GetBatchedBalance(wallets)  # Single API call
   ```

### Problem: SSL/TLS Issues

**Symptoms:**
```
ssl.SSLError
certificate verify failed
```

**Solutions:**

1. **Update Certificates:**
   ```bash
   # macOS
   /Applications/Python\ 3.x/Install\ Certificates.command
   
   # Linux
   sudo apt-get update && sudo apt-get install ca-certificates
   
   # Python
   pip install --upgrade certifi
   ```

2. **Verify SSL:**
   ```python
   import ssl
   import socket
   
   def check_ssl(hostname, port=443):
       context = ssl.create_default_context()
       with socket.create_connection((hostname, port)) as sock:
           with context.wrap_socket(sock, server_hostname=hostname) as ssock:
               print(f"SSL certificate for {hostname} is valid")
               return True
   
   check_ssl("axiom.trade")
   ```

---

## 📡 WebSocket Issues

### Problem: WebSocket Connection Drops

**Symptoms:**
```
ConnectionClosed: no close frame received or sent
WebSocket connection lost
```

**Solutions:**

1. **Implement Reconnection Logic:**
   ```python
   import asyncio
   import logging
   
   class ReconnectingWebSocket:
       def __init__(self, client, max_retries=5):
           self.client = client
           self.max_retries = max_retries
           self.retry_count = 0
           self.is_connected = False
       
       async def connect_with_retry(self):
           while self.retry_count < self.max_retries:
               try:
                   await self.client.ws.connect()
                   self.is_connected = True
                   self.retry_count = 0
                   logging.info("WebSocket connected successfully")
                   return True
               except Exception as e:
                   self.retry_count += 1
                   wait_time = min(30, 2 ** self.retry_count)
                   logging.warning(f"WebSocket connection failed (attempt {self.retry_count}): {e}")
                   logging.info(f"Retrying in {wait_time} seconds...")
                   await asyncio.sleep(wait_time)
           
           logging.error("Max retry attempts reached")
           return False
       
       async def monitor_connection(self):
           while True:
               if not self.is_connected:
                   await self.connect_with_retry()
               await asyncio.sleep(10)
   ```

2. **Heartbeat/Ping Implementation:**
   ```python
   async def websocket_heartbeat(ws_client):
       while True:
           try:
               await ws_client.ping()
               await asyncio.sleep(30)  # Ping every 30 seconds
           except Exception as e:
               logging.warning(f"Heartbeat failed: {e}")
               break
   ```

### Problem: Subscription Failures

**Symptoms:**
```
Failed to subscribe to channel
No data received after subscription
```

**Diagnostic Steps:**

1. **Test WebSocket Connection:**
   ```python
   async def test_websocket():
       try:
           client = AxiomTradeClient(
               auth_token=Config.AUTH_TOKEN,
               refresh_token=Config.REFRESH_TOKEN
           )
           
           await client.ws.connect()
           print("✅ WebSocket connection successful")
           
           # Test subscription
           await client.subscribe_new_tokens(lambda tokens: print(f"Received {len(tokens)} tokens"))
           print("✅ Subscription successful")
           
       except Exception as e:
           print(f"❌ WebSocket test failed: {e}")
   
   asyncio.run(test_websocket())
   ```

**Solutions:**

1. **Verify Authentication:**
   ```python
   # Check if tokens are valid for WebSocket
   if not Config.AUTH_TOKEN or not Config.REFRESH_TOKEN:
       print("❌ WebSocket requires authentication tokens")
       print("Please follow the authentication guide")
   ```

2. **Check Subscription Parameters:**
   ```python
   async def debug_subscription():
       try:
           # Add debug logging
           logging.getLogger("axiomtradeapi").setLevel(logging.DEBUG)
           
           client = AxiomTradeClient(
               auth_token=Config.AUTH_TOKEN,
               refresh_token=Config.REFRESH_TOKEN,
               log_level=logging.DEBUG
           )
           
           await client.subscribe_new_tokens(lambda tokens: print(f"Debug: {tokens}"))
           
       except Exception as e:
           logging.error(f"Subscription debug failed: {e}")
   ```

---

## ⚡ Performance Issues

### Problem: Slow API Responses

**Symptoms:**
- API calls taking longer than expected
- Timeout errors
- Poor application performance

**Diagnostic Tools:**

```python
import time
import statistics

class PerformanceMonitor:
    def __init__(self):
        self.response_times = []
    
    def measure_call(self, func, *args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            return result
        except Exception as e:
            response_time = time.time() - start_time
            print(f"Call failed after {response_time:.3f}s: {e}")
            raise
    
    def get_stats(self):
        if not self.response_times:
            return "No data"
        
        return {
            'count': len(self.response_times),
            'avg': statistics.mean(self.response_times),
            'min': min(self.response_times),
            'max': max(self.response_times),
            'median': statistics.median(self.response_times)
        }

# Usage
monitor = PerformanceMonitor()
balance = monitor.measure_call(client.GetBalance, wallet_address)
print(f"Performance stats: {monitor.get_stats()}")
```

**Solutions:**

1. **Use Connection Pooling:**
   ```python
   import aiohttp
   
   class OptimizedClient:
       def __init__(self):
           self.session = None
       
       async def __aenter__(self):
           connector = aiohttp.TCPConnector(
               limit=100,
               limit_per_host=30,
               keepalive_timeout=30
           )
           self.session = aiohttp.ClientSession(connector=connector)
           return self
       
       async def __aexit__(self, exc_type, exc_val, exc_tb):
           await self.session.close()
   ```

2. **Implement Caching:**
   ```python
   import time
   from functools import wraps
   
   def cache_result(ttl=60):
       """Cache results for specified TTL in seconds"""
       cache = {}
       
       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               key = str(args) + str(kwargs)
               now = time.time()
               
               if key in cache:
                   result, timestamp = cache[key]
                   if now - timestamp < ttl:
                       return result
               
               result = func(*args, **kwargs)
               cache[key] = (result, now)
               return result
           
           return wrapper
       return decorator
   
   # Usage
   @cache_result(ttl=30)  # Cache for 30 seconds
   def cached_get_balance(wallet):
       return client.GetBalance(wallet)
   ```

### Problem: High Memory Usage

**Symptoms:**
- Application consuming excessive RAM
- Out of memory errors
- System slowdown

**Diagnostic Tools:**

```python
import psutil
import os

def monitor_memory_usage():
    """Monitor memory usage of current process"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    print(f"RSS (Physical Memory): {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS (Virtual Memory): {memory_info.vms / 1024 / 1024:.2f} MB")
    print(f"Memory Percent: {process.memory_percent():.2f}%")

# Call periodically
import threading
import time

def memory_monitor_thread():
    while True:
        monitor_memory_usage()
        time.sleep(60)  # Check every minute

threading.Thread(target=memory_monitor_thread, daemon=True).start()
```

**Solutions:**

1. **Limit Data Retention:**
   ```python
   from collections import deque
   
   class MemoryEfficientBot:
       def __init__(self):
           # Use deque with maxlen to limit memory
           self.recent_tokens = deque(maxlen=1000)
           self.price_history = deque(maxlen=10000)
       
       def process_token(self, token):
           self.recent_tokens.append(token)
           # Old items automatically removed when maxlen exceeded
   ```

2. **Garbage Collection:**
   ```python
   import gc
   
   def periodic_cleanup():
       """Periodically force garbage collection"""
       collected = gc.collect()
       print(f"Garbage collected: {collected} objects")
   
   # Call periodically in your main loop
   asyncio.create_task(self.periodic_cleanup_task())
   ```

---

## 🐛 Common Error Messages

### "Invalid wallet address format"

**Error:**
```python
ValueError: Invalid Solana address: abc123
```

**Solution:**
```python
def validate_solana_address(address):
    """Validate Solana wallet address"""
    if not address:
        raise ValueError("Address cannot be empty")
    
    if len(address) != 44:
        raise ValueError(f"Solana addresses must be 44 characters, got {len(address)}")
    
    # Check for valid base58 characters
    import string
    valid_chars = string.ascii_letters + string.digits
    valid_chars = valid_chars.replace('0', '').replace('O', '').replace('I', '').replace('l')
    
    if not all(c in valid_chars for c in address):
        raise ValueError("Address contains invalid characters")
    
    return True

# Usage
try:
    validate_solana_address(wallet_address)
    balance = client.GetBalance(wallet_address)
except ValueError as e:
    print(f"Invalid address: {e}")
```

### "No active WebSocket connection"

**Error:**
```python
RuntimeError: No active WebSocket connection
```

**Solution:**
```python
async def ensure_websocket_connection(client):
    """Ensure WebSocket is connected before use"""
    if not hasattr(client, 'ws') or not client.ws.is_connected:
        print("Establishing WebSocket connection...")
        await client.ws.connect()
        
        # Wait for connection to be fully established
        await asyncio.sleep(1)
    
    return client

# Usage
client = await ensure_websocket_connection(client)
await client.subscribe_new_tokens(callback)
```

### "JSON decode error"

**Error:**
```python
json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Solution:**
```python
def safe_json_parse(response_text):
    """Safely parse JSON response"""
    try:
        if not response_text.strip():
            return {"error": "Empty response"}
        
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response text: {response_text[:200]}...")
        return {"error": "Invalid JSON response"}

# Add to your API calls
response_data = safe_json_parse(response.text)
```

---

## 🔧 Debug Mode

Enable comprehensive debugging for troubleshooting:

```python
import logging
import sys

def enable_debug_mode():
    """Enable comprehensive debug logging"""
    
    # Set up detailed logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler('debug.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Enable debug for specific modules
    logging.getLogger('axiomtradeapi').setLevel(logging.DEBUG)
    logging.getLogger('websockets').setLevel(logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.DEBUG)
    
    print("🐛 Debug mode enabled - check debug.log for detailed logs")

# Enable before creating client
enable_debug_mode()
client = AxiomTradeClient(log_level=logging.DEBUG)
```

## 📊 System Health Check

Create a comprehensive health check script:

```python
#!/usr/bin/env python3
"""
Comprehensive system health check for AxiomTradeAPI-py
"""

import asyncio
import json
import platform
import sys
import time
from datetime import datetime

async def run_health_check():
    """Run comprehensive health check"""
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'system_info': {},
        'python_info': {},
        'network_tests': {},
        'api_tests': {},
        'recommendations': []
    }
    
    print("🏥 AxiomTradeAPI-py Health Check")
    print("=" * 50)
    
    # System Information
    results['system_info'] = {
        'platform': platform.platform(),
        'python_version': sys.version,
        'architecture': platform.architecture()[0]
    }
    
    print(f"🖥️  System: {platform.platform()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Python version check
    if sys.version_info < (3, 8):
        results['recommendations'].append("Upgrade Python to 3.8 or higher")
        print("⚠️  Warning: Python 3.8+ required")
    else:
        print("✅ Python version OK")
    
    # Package installation test
    try:
        import axiomtradeapi
        print(f"✅ AxiomTradeAPI-py imported successfully")
        results['api_tests']['import'] = True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        results['api_tests']['import'] = False
        results['recommendations'].append("Run: pip install axiomtradeapi")
    
    # Network connectivity test
    try:
        import requests
        response = requests.get("https://axiom.trade", timeout=10)
        results['network_tests']['axiom_trade_reachable'] = response.status_code == 200
        print(f"✅ Axiom Trade reachable (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Network test failed: {e}")
        results['network_tests']['axiom_trade_reachable'] = False
        results['recommendations'].append("Check internet connection")
    
    # API functionality test
    if results['api_tests'].get('import'):
        try:
            from axiomtradeapi import AxiomTradeClient
            client = AxiomTradeClient()
            
            # Test balance query
            test_wallet = "BJBgjyDZx5FSsyJf6bFKVXuJV7DZY9PCSMSi5d9tcEVh"
            balance = client.GetBalance(test_wallet)
            
            results['api_tests']['balance_query'] = True
            print(f"✅ API test successful - Balance: {balance['sol']} SOL")
        except Exception as e:
            print(f"❌ API test failed: {e}")
            results['api_tests']['balance_query'] = False
            results['recommendations'].append("Check API connectivity and authentication")
    
    # Configuration check
    try:
        from config import Config
        has_auth = bool(Config.AUTH_TOKEN and Config.REFRESH_TOKEN)
        results['api_tests']['authentication_configured'] = has_auth
        
        if has_auth:
            print("✅ Authentication configured")
        else:
            print("⚠️  Authentication not configured (WebSocket features unavailable)")
            results['recommendations'].append("Set up authentication tokens for WebSocket features")
    except ImportError:
        print("⚠️  No config.py found")
        results['recommendations'].append("Create config.py with your settings")
    
    # Memory usage check
    try:
        import psutil
        memory_percent = psutil.virtual_memory().percent
        results['system_info']['memory_usage_percent'] = memory_percent
        
        if memory_percent > 90:
            print(f"⚠️  High memory usage: {memory_percent:.1f}%")
            results['recommendations'].append("Consider closing other applications")
        else:
            print(f"✅ Memory usage OK: {memory_percent:.1f}%")
    except ImportError:
        print("ℹ️  Install psutil for memory monitoring: pip install psutil")
    
    # Final summary
    print("\n📊 Health Check Summary:")
    print("=" * 30)
    
    total_tests = len([v for v in results['api_tests'].values() if isinstance(v, bool)])
    passed_tests = sum(results['api_tests'].values())
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
    
    if results['recommendations']:
        print("\n💡 Recommendations:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"   {i}. {rec}")
    else:
        print("\n🎉 All checks passed! Your system is ready for trading.")
    
    # Save results
    with open('health_check_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: health_check_results.json")

if __name__ == "__main__":
    asyncio.run(run_health_check())
```

---

## 🆘 Getting Additional Help

If you're still experiencing issues after trying these solutions:

### 1. Community Support

- **Discord**: [Join our community](https://discord.gg/p7YyFqSmAz) for real-time help
- **GitHub**: [File an issue](https://github.com/ChipaDevTeam/AxiomTradeAPI-py/issues) with details

### 2. Professional Support

- **Custom Development**: [Professional bot development](https://shop.chipatrade.com/products/create-your-bot)
- **Priority Support**: Available with professional services

### 3. When Reporting Issues

Please include:

1. **System Information**:
   ```bash
   python --version
   pip list | grep axiom
   uname -a  # Linux/Mac
   ```

2. **Error Details**:
   - Full error message and stack trace
   - Steps to reproduce the issue
   - Expected vs actual behavior

3. **Code Sample**:
   - Minimal code that reproduces the issue
   - Remove any sensitive information (tokens, private keys)

4. **Environment**:
   - Operating system and version
   - Network configuration (proxy, firewall)
   - Python virtual environment details

### 4. Documentation Resources

- **API Reference**: [Complete API documentation](./api-reference.md)
- **Getting Started**: [Beginner's guide](./getting-started.md)
- **Advanced Guides**: [Trading bots and optimization](./trading-bots.md)

---

## 📋 Maintenance Checklist

Regular maintenance tasks to prevent issues:

### Daily
- [ ] Check bot logs for errors
- [ ] Monitor memory usage
- [ ] Verify API connectivity

### Weekly
- [ ] Update dependencies if needed
- [ ] Review token expiration dates
- [ ] Clean up log files

### Monthly
- [ ] Run comprehensive health check
- [ ] Update AxiomTradeAPI-py to latest version
- [ ] Review and update security settings

---

*Need immediate help? Join our [Discord community](https://discord.gg/p7YyFqSmAz) for real-time support from experienced developers.*