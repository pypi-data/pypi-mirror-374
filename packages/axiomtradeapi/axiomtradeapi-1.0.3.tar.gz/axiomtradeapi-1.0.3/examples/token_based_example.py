#!/usr/bin/env python3
"""
Example script demonstrating the new token-based authentication for Axiom Trade API
This example shows how to use the API without requiring username/password in the constructor
"""

from axiomtradeapi import AxiomTradeClient
import json
import os

def main():
    print("Axiom Trade API - Token-Based Authentication Example")
    print("=" * 55)
    
    # Initialize client without any credentials
    client = AxiomTradeClient()
    
    print("\nOption 1: Fresh login with OTP")
    print("-" * 30)
    
    # Get user credentials
    email = input("Enter your email: ")
    b64_password = input("Enter your base64 encoded password: ")
    otp_code = input("Enter the OTP code sent to your email: ")
    
    try:
        # Complete login process
        login_result = client.login(email, b64_password, otp_code)
        
        print("✓ Login successful!")
        print(f"Access Token: {login_result.get('access_token', 'Not available')[:50]}...")
        print(f"Refresh Token: {login_result.get('refresh_token', 'Not available')[:50]}...")
        
        # Save tokens for future use (optional)
        tokens = client.get_tokens()
        print(f"\nTokens available: {client.is_authenticated()}")
        
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return
    
    print("\nOption 2: Using existing tokens")
    print("-" * 30)
    
    # Alternative: Initialize with existing tokens
    client2 = AxiomTradeClient()
    
    # Set tokens manually (you would get these from secure storage)
    access_token = input("Enter your access token (or press Enter to skip): ")
    refresh_token = input("Enter your refresh token (or press Enter to skip): ")
    
    if access_token and refresh_token:
        client2.set_tokens(access_token=access_token, refresh_token=refresh_token)
        print(f"✓ Tokens set manually. Authenticated: {client2.is_authenticated()}")
    
    print("\nTesting API functionality...")
    print("-" * 30)
    
    # Test trending tokens with authenticated client
    try:
        trending_tokens = client.get_trending_tokens('1h')
        print("✓ Successfully fetched trending tokens:")
        print(json.dumps(trending_tokens, indent=2)[:500] + "...")
        
    except Exception as e:
        print(f"✗ Failed to fetch trending tokens: {e}")
    
    print("\nToken refresh example...")
    print("-" * 30)
    
    # Test token refresh
    try:
        if client.refresh_token:
            new_access_token = client.refresh_access_token()
            print(f"✓ Access token refreshed: {new_access_token[:50]}...")
        else:
            print("✗ No refresh token available for refresh")
            
    except Exception as e:
        print(f"✗ Token refresh failed: {e}")

if __name__ == "__main__":
    main()
