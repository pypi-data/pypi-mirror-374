import asyncio
import logging
from axiomtradeapi.websocket._client import AxiomTradeWebSocketClient

async def handle_new_tokens(tokens):
    """Handle new token updates."""
    for token in tokens:
        print(f"\nNew Token Detected:")
        print(f"Name: {token['tokenName']} ({token['tokenTicker']})")
        print(f"Address: {token['tokenAddress']}")
        print(f"Protocol: {token['protocol']}")
        print(f"Market Cap: {token['marketCapSol']} SOL")
        print(f"Volume: {token['volumeSol']} SOL")
        if token['website']:
            print(f"Website: {token['website']}")
        if token['twitter']:
            print(f"Twitter: {token['twitter']}")
        if token['telegram']:
            print(f"Telegram: {token['telegram']}")
        print("-" * 50)

async def main():
    # Note: WebSocket requires authentication tokens for full functionality
    # For testing purposes, we'll try to connect without tokens first
    # If you have tokens, uncomment the lines below:
    
    # auth_token = "your_auth_token_here"
    # refresh_token = "your_refresh_token_here" 
    # client = AxiomTradeWebSocketClient(
    #     auth_token=auth_token,
    #     refresh_token=refresh_token,
    #     log_level=logging.DEBUG
    # )
    
    # Initialize client with debug logging (no auth for testing)
    client = AxiomTradeWebSocketClient(log_level=logging.DEBUG)
    
    try:
        # Subscribe to new token updates
        success = await client.subscribe_new_tokens(handle_new_tokens)
        
        if success:
            print("Successfully subscribed to new tokens")
            # Start listening for updates
            await client.start()
        else:
            print("Failed to subscribe. This may be due to missing authentication.")
            print("WebSocket connections to Axiom Trade require valid auth tokens.")
            print("Please refer to the authentication guide for setup instructions.")
            
    except Exception as e:
        print(f"Connection failed: {e}")
        print("This is likely due to missing authentication tokens.")
        print("WebSocket features require valid auth-access-token and auth-refresh-token.")
        print("Please check the troubleshooting guide for authentication setup.")

if __name__ == "__main__":
    asyncio.run(main())
