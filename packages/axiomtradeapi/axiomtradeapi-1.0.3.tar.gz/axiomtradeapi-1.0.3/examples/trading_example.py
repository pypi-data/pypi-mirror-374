#!/usr/bin/env python3
"""
Example script demonstrating how to use the AxiomTradeAPI client 
for buying and selling tokens on Solana.
"""

import asyncio
import logging
from axiomtradeapi import AxiomTradeClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Initialize the client with your credentials
    # Replace with your actual username and password
    client = AxiomTradeClient(
        username="your_email@example.com",
        password="your_password",
        log_level=logging.INFO
    )
    
    # Example private key (replace with your actual private key)
    # This is just an example format - use your real private key
    private_key = "your_private_key_here"  # Base58 encoded private key
    
    # Example token mint address (replace with actual token you want to trade)
    token_mint = "So11111111111111111111111111111111111111112"  # Example: Wrapped SOL
    
    # Your wallet address (derived from private key)
    wallet_address = "your_wallet_address_here"
    
    try:
        # Example 1: Check SOL balance
        logger.info("Checking SOL balance...")
        balance = client.GetBalance(wallet_address)
        if balance:
            logger.info(f"Current SOL balance: {balance['sol']} SOL")
        
        # Example 2: Check token balance
        logger.info("Checking token balance...")
        token_balance = client.get_token_balance(wallet_address, token_mint)
        if token_balance is not None:
            logger.info(f"Current token balance: {token_balance}")
        
        # Example 3: Buy tokens
        logger.info("Placing buy order...")
        buy_result = client.buy_token(
            private_key=private_key,
            token_mint=token_mint,
            amount_sol=0.1,  # Buy 0.1 SOL worth of tokens
            slippage_percent=5.0  # 5% slippage tolerance
        )
        
        if buy_result["success"]:
            logger.info(f"Buy order successful! Transaction: {buy_result['signature']}")
        else:
            logger.error(f"Buy order failed: {buy_result['error']}")
        
        # Example 4: Sell tokens (uncomment to use)
        # logger.info("Placing sell order...")
        # sell_result = client.sell_token(
        #     private_key=private_key,
        #     token_mint=token_mint,
        #     amount_tokens=1000,  # Sell 1000 tokens
        #     slippage_percent=5.0  # 5% slippage tolerance
        # )
        # 
        # if sell_result["success"]:
        #     logger.info(f"Sell order successful! Transaction: {sell_result['signature']}")
        # else:
        #     logger.error(f"Sell order failed: {sell_result['error']}")
        
        # Example 5: Subscribe to new tokens (WebSocket)
        logger.info("Subscribing to new tokens...")
        
        def on_new_token(token_data):
            logger.info(f"New token detected: {token_data}")
        
        await client.subscribe_new_tokens(on_new_token)
        
        # Keep the connection alive for a few seconds to receive updates
        await asyncio.sleep(10)
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        # Clean up WebSocket connection
        if hasattr(client, 'ws') and client.ws:
            await client.ws.close()

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
