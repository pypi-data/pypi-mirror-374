# Automatic Token Refresh and Secure Storage

This document describes the new automatic token refresh and secure storage features in the AxiomTradeAPI-py library.

## Overview

The library now includes:
- **Automatic token refresh** using the correct API endpoint
- **Secure token storage** with encryption
- **Automatic token management** with configurable options
- **Backward compatibility** with existing code

## Key Features

### 1. Automatic Token Refresh

The library automatically refreshes your access tokens when they expire, using the correct API endpoint:
- Endpoint: `https://api.axiom.trade/refresh-access-token`
- Uses proper headers and cookies as required by the API
- Handles both cookie-based and JSON-based responses
- Automatically saves refreshed tokens (when enabled)

### 2. Secure Token Storage

Tokens are stored securely on your local machine:
- **Location**: `~/.axiomtradeapi/` directory (Windows: `C:\Users\{username}\.axiomtradeapi\`)
- **Encryption**: Uses Fernet symmetric encryption from the `cryptography` library
- **Permissions**: Files are readable only by your user account
- **Format**: Encrypted JSON files

### 3. Configurable Options

You can control how tokens are managed:
- `use_saved_tokens=True`: Enable automatic token loading/saving (default)
- `use_saved_tokens=False`: Disable automatic token storage
- `storage_dir`: Custom directory for token storage

## Usage Examples

### Basic Usage with Automatic Token Management

```python
from axiomtradeapi.client import AxiomTradeClient

# Create client with automatic token management (default behavior)
client = AxiomTradeClient(
    username="your_email@example.com",
    password="your_password",
    use_saved_tokens=True  # Default: automatically load/save tokens
)

# The client will:
# 1. Try to load saved tokens
# 2. Refresh them if expired
# 3. Login if no valid tokens exist
# 4. Save new tokens automatically

# Make API calls - authentication is handled automatically
trending = client.get_trending_tokens()
```

### Manual Token Management

```python
from axiomtradeapi.client import AxiomTradeClient

# Disable automatic token storage
client = AxiomTradeClient(use_saved_tokens=False)

# Set tokens manually
client.set_tokens(
    access_token="your_access_token",
    refresh_token="your_refresh_token"
)

# Manually refresh when needed
if not client.is_authenticated():
    client.refresh_access_token()
```

### Using Environment Variables

```python
import os
from axiomtradeapi.client import AxiomTradeClient

# Load tokens from environment
client = AxiomTradeClient(
    auth_token=os.getenv('ACCESS_TOKEN'),
    refresh_token=os.getenv('REFRESH_TOKEN'),
    use_saved_tokens=False  # Don't save env tokens
)
```

### Advanced Authentication Management

```python
from axiomtradeapi.auth.auth_manager import AuthManager

# Create auth manager with custom settings
auth_manager = AuthManager(
    username="your_email@example.com",
    password="your_password",
    storage_dir="/custom/path",  # Custom storage location
    use_saved_tokens=True
)

# Check token status
token_info = auth_manager.get_token_info()
print(f"Authenticated: {token_info['authenticated']}")
print(f"Expires in: {token_info['time_until_expiry']} seconds")

# Force token refresh
if auth_manager.refresh_tokens():
    print("Tokens refreshed successfully!")

# Ensure valid authentication (auto-refresh/login as needed)
if auth_manager.ensure_valid_authentication():
    print("Ready to make API calls!")
```

## API Reference

### AxiomTradeClient

#### Constructor Parameters
- `username` (str, optional): Email for automatic login
- `password` (str, optional): Password for automatic login
- `auth_token` (str, optional): Existing access token
- `refresh_token` (str, optional): Existing refresh token
- `storage_dir` (str, optional): Custom directory for token storage
- `use_saved_tokens` (bool, default=True): Enable automatic token loading/saving

#### Methods

##### Authentication Methods
- `login(email, password)`: Login with credentials
- `set_tokens(access_token, refresh_token)`: Set tokens manually
- `is_authenticated()`: Check if client has valid tokens
- `refresh_access_token()`: Manually refresh access token
- `ensure_authenticated()`: Ensure valid authentication (auto-refresh/login)
- `logout()`: Clear all authentication data

##### Token Management Methods
- `get_tokens()`: Get current token information
- `get_token_info_detailed()`: Get detailed token status
- `clear_saved_tokens()`: Clear saved tokens from storage
- `has_saved_tokens()`: Check if saved tokens exist

### AuthManager

#### Constructor Parameters
- `username` (str, optional): Email for automatic login
- `password` (str, optional): Password for automatic login
- `auth_token` (str, optional): Existing access token
- `refresh_token` (str, optional): Existing refresh token
- `storage_dir` (str, optional): Custom directory for token storage
- `use_saved_tokens` (bool, default=True): Enable automatic token loading/saving

#### Methods
- `authenticate()`: Perform full login flow
- `refresh_tokens()`: Refresh access token
- `ensure_valid_authentication()`: Ensure valid tokens (auto-refresh/login)
- `get_token_info()`: Get detailed token information
- `logout()`: Clear all authentication data
- `clear_saved_tokens()`: Clear saved tokens
- `has_saved_tokens()`: Check if saved tokens exist

## Security Considerations

### Token Storage Security
- Tokens are encrypted using Fernet symmetric encryption
- Encryption key is stored separately and is user-specific
- File permissions are set to be readable only by the user
- Storage directory is created with restricted permissions

### Best Practices
1. **Use automatic token management** for most applications
2. **Disable token storage** (`use_saved_tokens=False`) for:
   - Shared environments
   - CI/CD pipelines
   - When using external token management
3. **Set custom storage directory** for applications with specific security requirements
4. **Clear tokens on logout** to prevent unauthorized access

## Error Handling

The library provides comprehensive error handling:

```python
from axiomtradeapi.client import AxiomTradeClient

client = AxiomTradeClient()

try:
    # This will automatically handle token refresh
    if client.ensure_authenticated():
        trending = client.get_trending_tokens()
    else:
        print("Authentication failed")
except Exception as e:
    print(f"Error: {e}")
```

## Migration from Previous Versions

The new version is backward compatible:

```python
# Old way (still works)
from axiomtradeapi.client import AxiomTradeClient
client = AxiomTradeClient()
client.set_tokens("access_token", "refresh_token")

# New way (recommended)
from axiomtradeapi.client import AxiomTradeClient
client = AxiomTradeClient(
    auth_token="access_token",
    refresh_token="refresh_token"
)
# Tokens are now automatically managed
```

## Environment Variables

You can use environment variables for configuration:

```bash
# Windows PowerShell
$env:ACCESS_TOKEN="your_access_token"
$env:REFRESH_TOKEN="your_refresh_token"

# Windows Command Prompt
set ACCESS_TOKEN=your_access_token
set REFRESH_TOKEN=your_refresh_token

# Linux/macOS
export ACCESS_TOKEN="your_access_token"
export REFRESH_TOKEN="your_refresh_token"
```

```python
import os
from axiomtradeapi.client import AxiomTradeClient

client = AxiomTradeClient(
    auth_token=os.getenv('ACCESS_TOKEN'),
    refresh_token=os.getenv('REFRESH_TOKEN')
)
```

## Troubleshooting

### Common Issues

1. **Tokens not being saved**
   - Check if `use_saved_tokens=True` (default)
   - Verify directory permissions
   - Check available disk space

2. **Token refresh fails**
   - Verify refresh token is valid
   - Check network connectivity
   - Review error logs for specific issues

3. **Permission errors**
   - Ensure user has write access to storage directory
   - Check if storage directory exists and is accessible

### Debug Logging

Enable debug logging to see what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from axiomtradeapi.client import AxiomTradeClient
client = AxiomTradeClient()
```

This will show detailed information about:
- Token loading/saving operations
- Refresh attempts
- Authentication status
- API requests

## Dependencies

The new features require the `cryptography` library:

```bash
pip install cryptography>=3.4.8
```

This is automatically included when you install the updated package.
