#!/usr/bin/env python3
"""
Secure Token Management Example
Demonstrates automatic token refresh and secure storage features
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from axiomtradeapi.client import AxiomTradeClient
from axiomtradeapi.auth.auth_manager import create_authenticated_session

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_with_saved_tokens():
    """Example using automatic token saving/loading"""
    print("=== Example 1: Automatic Token Management ===")
    
    # Create client with automatic token saving enabled (default)
    client = AxiomTradeClient(
        username="your_email@example.com",  # Replace with your email
        password="your_password",           # Replace with your password
        use_saved_tokens=True              # Default: automatically load/save tokens
    )
    
    # Check if we have saved tokens
    if client.has_saved_tokens():
        print("✅ Found saved tokens, attempting to use them...")
        
        # Check token status
        token_info = client.get_token_info_detailed()
        print(f"Token status: {'Valid' if not token_info.get('is_expired', True) else 'Expired'}")
        
        if token_info.get('is_expired', True):
            print("🔄 Tokens expired, will attempt refresh...")
    else:
        print("ℹ️ No saved tokens found, will need to login")
    
    # Try to ensure authentication (will auto-refresh if needed)
    if client.ensure_authenticated():
        print("✅ Authentication successful!")
        
        # Now you can make API calls
        try:
            trending = client.get_trending_tokens()
            print(f"Successfully fetched {len(trending.get('tokens', []))} trending tokens")
        except Exception as e:
            print(f"❌ API call failed: {e}")
    else:
        print("❌ Authentication failed")


def example_without_saved_tokens():
    """Example with token saving disabled"""
    print("\n=== Example 2: No Token Saving ===")
    
    # Create client with token saving disabled
    client = AxiomTradeClient(
        username="your_email@example.com",  # Replace with your email
        password="your_password",           # Replace with your password
        use_saved_tokens=False              # Disable automatic token saving
    )
    
    print("🔒 Token saving disabled - tokens will not be stored")
    
    # You'll need to login each time
    try:
        login_result = client.login()
        if login_result.get('success'):
            print("✅ Login successful (tokens not saved)")
        else:
            print("❌ Login failed")
    except Exception as e:
        print(f"❌ Login error: {e}")


def example_manual_token_management():
    """Example with manual token management"""
    print("\n=== Example 3: Manual Token Management ===")
    
    # Create client without credentials
    client = AxiomTradeClient(use_saved_tokens=False)
    
    # Manually set tokens (e.g., from external source)
    access_token = "your_access_token_here"    # Replace with actual token
    refresh_token = "your_refresh_token_here"  # Replace with actual token
    
    if access_token != "your_access_token_here":  # Only if real tokens provided
        client.set_tokens(access_token, refresh_token)
        print("✅ Tokens set manually")
        
        # Test token refresh
        if client.refresh_access_token():
            print("✅ Token refresh successful")
        else:
            print("❌ Token refresh failed")
    else:
        print("ℹ️ Please provide real tokens to test manual management")


def example_clear_saved_tokens():
    """Example showing how to clear saved tokens"""
    print("\n=== Example 4: Clear Saved Tokens ===")
    
    client = AxiomTradeClient()
    
    if client.has_saved_tokens():
        print("📁 Found saved tokens")
        
        # Clear saved tokens
        if client.clear_saved_tokens():
            print("🗑️ Saved tokens cleared successfully")
        else:
            print("❌ Failed to clear saved tokens")
    else:
        print("ℹ️ No saved tokens to clear")


def example_token_info():
    """Example showing token information"""
    print("\n=== Example 5: Token Information ===")
    
    client = AxiomTradeClient(use_saved_tokens=True)
    
    # Get detailed token information
    token_info = client.get_token_info_detailed()
    
    if token_info.get('authenticated'):
        print("📊 Token Information:")
        print(f"  - Authenticated: ✅")
        print(f"  - Access Token: {token_info.get('access_token_preview', 'N/A')}")
        print(f"  - Expires At: {token_info.get('expires_at', 'N/A')}")
        print(f"  - Is Expired: {'❌ Yes' if token_info.get('is_expired') else '✅ No'}")
        print(f"  - Needs Refresh: {'🔄 Yes' if token_info.get('needs_refresh') else '✅ No'}")
        
        time_until_expiry = token_info.get('time_until_expiry', 0)
        if time_until_expiry > 0:
            hours = int(time_until_expiry // 3600)
            minutes = int((time_until_expiry % 3600) // 60)
            print(f"  - Time Until Expiry: {hours}h {minutes}m")
    else:
        print("❌ Not authenticated")


def main():
    """Run all examples"""
    print("🚀 Axiom Trade API - Secure Token Management Examples")
    print("=" * 60)
    
    try:
        # Run examples
        example_with_saved_tokens()
        example_without_saved_tokens()
        example_manual_token_management()
        example_clear_saved_tokens()
        example_token_info()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed!")
        print("\n📝 Notes:")
        print("  - Tokens are stored securely in ~/.axiomtradeapi/")
        print("  - Tokens are encrypted using the cryptography library")
        print("  - Only you can access the stored tokens")
        print("  - Set use_saved_tokens=False to disable automatic token storage")
        print("  - Tokens are automatically refreshed when needed")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
