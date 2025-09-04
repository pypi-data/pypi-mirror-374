#!/usr/bin/env python3
"""
Example script demonstrating Axiom Trade API login and trending tokens functionality
Updated to show the new token-based authentication approach
"""

from axiomtradeapi import AxiomTradeClient
import json

def main():
    print("Axiom Trade API - Login and Trending Tokens Example")
    print("=" * 55)
    
    # Initialize client (NEW: No credentials required in constructor)
    client = AxiomTradeClient()
    
    # Option 1: Fresh login with OTP (NEW: Simplified login method)
    print("\nOption 1: Complete login process (New Method)")
    email = input("Enter your email: ")
    b64_password = input("Enter your base64 encoded password: ")
    otp_code = input("Enter the OTP code: ")
    
    try:
        # NEW: Single login method that handles the entire process
        login_result = client.login(email, b64_password, otp_code)
        
        print("✓ Login successful!")
        print(f"Access Token: {login_result.get('access_token', 'Not available')[:50]}...")
        print(f"Refresh Token: {login_result.get('refresh_token', 'Not available')[:50]}...")
        
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return
        print(f"Client Secret: {credentials.get('clientSecret', 'N/A')}")
        print(f"Org ID: {credentials.get('orgId', 'N/A')}")
        print(f"User ID: {credentials.get('userId', 'N/A')}")
        
    except Exception as e:
        print(f"✗ Login failed: {e}")
        
        # Option 2: Use existing tokens
        print("\nOption 2: Using existing tokens")
        use_existing = input("Do you have existing access/refresh tokens? (y/n): ").lower().strip() == 'y'
        
        if use_existing:
            access_token = input("Enter your access token: ")
            refresh_token = input("Enter your refresh token (optional): ")
            
            if refresh_token:
                try:
                    # Try to refresh the access token
                    new_access_token = client.refresh_access_token_direct(refresh_token)
                    if new_access_token:
                        access_token = new_access_token
                        print("✓ Access token refreshed successfully")
                except Exception as e:
                    print(f"⚠ Could not refresh token: {e}")
                    print("Using provided access token instead")
            
            # Test trending tokens
            try:
                time_period = input("Enter time period (1h, 24h, 7d) [default: 1h]: ").strip() or '1h'
                trending = client.get_trending_tokens(access_token, time_period)
                
                print(f"\n📈 Trending tokens for {time_period}:")
                print("=" * 40)
                print(json.dumps(trending, indent=2))
                
            except Exception as e:
                print(f"✗ Failed to fetch trending tokens: {e}")
        else:
            print("Please obtain valid tokens to continue.")
            return

def interactive_demo():
    """Interactive demo for testing the API"""
    client = AxiomTradeClient()
    
    while True:
        print("\n" + "=" * 50)
        print("Axiom Trade API Interactive Demo")
        print("=" * 50)
        print("1. Login with email/password + OTP")
        print("2. Refresh access token")
        print("3. Get trending tokens")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == '1':
            try:
                email = input("Email: ")
                b64_password = input("Base64 password: ")
                
                otp_token = client.login_step1(email, b64_password)
                print("OTP sent! Check your email/phone.")
                
                otp_code = input("Enter OTP code: ")
                credentials = client.complete_login(email, b64_password, otp_code)
                
                print("Login successful!")
                print(json.dumps(credentials, indent=2))
                
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == '2':
            try:
                refresh_token = input("Refresh token: ")
                new_token = client.refresh_access_token_direct(refresh_token)
                print(f"New access token: {new_token}")
                
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == '3':
            try:
                access_token = input("Access token: ")
                time_period = input("Time period (1h/24h/7d) [1h]: ").strip() or '1h'
                
                trending = client.get_trending_tokens(access_token, time_period)
                print("\nTrending tokens:")
                print(json.dumps(trending, indent=2))
                
            except Exception as e:
                print(f"Error: {e}")
                
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_demo()
    else:
        main()
