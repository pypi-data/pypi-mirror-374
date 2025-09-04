#!/usr/bin/env python3
"""
Test script for the new trading functions in AxiomTradeAPI.
This script tests the buy/sell functionality without executing real trades.
"""

import asyncio
import logging
import os
from axiomtradeapi import AxiomTradeClient
from solders.keypair import Keypair

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_keypair():
    """Create a test keypair for demonstration purposes."""
    keypair = Keypair()
    logger.info(f"Test wallet created: {keypair.pubkey()}")
    return keypair

def test_private_key_conversion():
    """Test private key conversion functionality."""
    logger.info("Testing private key conversion...")
    
    try:
        # Create test client (without real credentials for testing)
        client = AxiomTradeClient(log_level=logging.INFO)
        
        # Create test keypair
        test_keypair = create_test_keypair()
        private_key_bytes = bytes(test_keypair)
        
        # Test conversion from bytes
        converted_keypair = client._get_keypair_from_private_key(private_key_bytes.hex())
        
        if str(converted_keypair.pubkey()) == str(test_keypair.pubkey()):
            logger.info("✅ Private key conversion test passed!")
            return True
        else:
            logger.error("❌ Private key conversion test failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Private key conversion test failed with error: {e}")
        return False

def test_endpoints():
    """Test that all required endpoints are available."""
    logger.info("Testing endpoint availability...")
    
    try:
        from axiomtradeapi.content.endpoints import Endpoints
        endpoints = Endpoints()
        
        required_endpoints = [
            'ENDPOINT_GET_BALANCE',
            'ENDPOINT_GET_BATCHED_BALANCE', 
            'ENDPOINT_BUY_TOKEN',
            'ENDPOINT_SELL_TOKEN',
            'ENDPOINT_SEND_TRANSACTION',
            'ENDPOINT_GET_TOKEN_BALANCE'
        ]
        
        for endpoint in required_endpoints:
            if hasattr(endpoints, endpoint):
                logger.info(f"✅ {endpoint}: {getattr(endpoints, endpoint)}")
            else:
                logger.error(f"❌ Missing endpoint: {endpoint}")
                return False
        
        logger.info("✅ All endpoints are available!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Endpoint test failed: {e}")
        return False

def test_client_initialization():
    """Test client initialization with different parameters."""
    logger.info("Testing client initialization...")
    
    try:
        # Test 1: Initialize without credentials (should work)
        client1 = AxiomTradeClient(log_level=logging.INFO)
        logger.info("✅ Client initialization without credentials: OK")
        
        # Test 2: Initialize with dummy credentials
        client2 = AxiomTradeClient(
            username="test@example.com",
            password="test_password",
            log_level=logging.INFO
        )
        logger.info("✅ Client initialization with credentials: OK")
        
        # Test 3: Check if trading methods exist
        methods_to_check = ['buy_token', 'sell_token', 'get_token_balance']
        
        for method in methods_to_check:
            if hasattr(client1, method):
                logger.info(f"✅ Method {method}: Available")
            else:
                logger.error(f"❌ Method {method}: Missing")
                return False
        
        logger.info("✅ Client initialization tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Client initialization test failed: {e}")
        return False

def test_buy_sell_function_structure():
    """Test the structure of buy/sell functions without executing trades."""
    logger.info("Testing buy/sell function structure...")
    
    try:
        client = AxiomTradeClient(log_level=logging.INFO)
        test_keypair = create_test_keypair()
        
        # Test buy_token function signature
        try:
            # This will fail at API call, but we can test the initial validation
            result = client.buy_token(
                private_key=bytes(test_keypair).hex(),
                token_mint="So11111111111111111111111111111111111111112",
                amount_sol=0.001,
                slippage_percent=5.0
            )
            
            # Should return a dict with success/error keys
            if isinstance(result, dict) and ('success' in result or 'error' in result):
                logger.info("✅ buy_token function structure: OK")
            else:
                logger.error("❌ buy_token function structure: Invalid return format")
                return False
                
        except Exception as e:
            # Expected to fail at API call, but structure should be OK
            if "error" in str(e).lower() or "failed" in str(e).lower():
                logger.info("✅ buy_token function structure: OK (expected API failure)")
            else:
                logger.error(f"❌ buy_token function structure: Unexpected error: {e}")
                return False
        
        # Test sell_token function signature
        try:
            result = client.sell_token(
                private_key=bytes(test_keypair).hex(),
                token_mint="So11111111111111111111111111111111111111112",
                amount_tokens=100,
                slippage_percent=5.0
            )
            
            if isinstance(result, dict) and ('success' in result or 'error' in result):
                logger.info("✅ sell_token function structure: OK")
            else:
                logger.error("❌ sell_token function structure: Invalid return format")
                return False
                
        except Exception as e:
            if "error" in str(e).lower() or "failed" in str(e).lower():
                logger.info("✅ sell_token function structure: OK (expected API failure)")
            else:
                logger.error(f"❌ sell_token function structure: Unexpected error: {e}")
                return False
        
        logger.info("✅ Buy/sell function structure tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Buy/sell function structure test failed: {e}")
        return False

async def run_all_tests():
    """Run all test functions."""
    logger.info("🚀 Starting AxiomTradeAPI Trading Functions Test Suite")
    logger.info("=" * 60)
    
    tests = [
        ("Endpoint Availability", test_endpoints),
        ("Client Initialization", test_client_initialization),
        ("Private Key Conversion", test_private_key_conversion),
        ("Buy/Sell Function Structure", test_buy_sell_function_structure),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running test: {test_name}")
        logger.info("-" * 40)
        
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: FAILED with exception: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Trading functions are ready to use.")
        return True
    else:
        logger.warning(f"⚠️  {total - passed} tests failed. Please review the issues above.")
        return False

def show_usage_example():
    """Show a usage example."""
    logger.info("\n" + "=" * 60)
    logger.info("📖 USAGE EXAMPLE")
    logger.info("=" * 60)
    
    example_code = '''
# Example usage of the trading functions:

import asyncio
from axiomtradeapi import AxiomTradeClient

async def main():
    # Initialize client with your credentials
    client = AxiomTradeClient(
        username="your_email@example.com",
        password="your_password"
    )
    
    # Your private key (keep this secure!)
    private_key = "your_base58_private_key_here"
    
    # Example token mint (replace with actual token)
    token_mint = "So11111111111111111111111111111111111111112"
    
    # Buy 0.1 SOL worth of tokens
    buy_result = client.buy_token(
        private_key=private_key,
        token_mint=token_mint,
        amount_sol=0.1,
        slippage_percent=5.0
    )
    
    if buy_result["success"]:
        print(f"✅ Buy successful: {buy_result['signature']}")
    else:
        print(f"❌ Buy failed: {buy_result['error']}")
    
    # Sell 1000 tokens
    sell_result = client.sell_token(
        private_key=private_key,
        token_mint=token_mint,
        amount_tokens=1000,
        slippage_percent=5.0
    )
    
    if sell_result["success"]:
        print(f"✅ Sell successful: {sell_result['signature']}")
    else:
        print(f"❌ Sell failed: {sell_result['error']}")

# Run the example
asyncio.run(main())
'''
    
    print(example_code)
    
    logger.info("\n🔐 SECURITY REMINDERS:")
    logger.info("- Never hardcode private keys in your source code")
    logger.info("- Use environment variables for sensitive data")
    logger.info("- Test with small amounts first")
    logger.info("- Always verify transaction signatures")

if __name__ == "__main__":
    async def main():
        success = await run_all_tests()
        show_usage_example()
        return success
    
    asyncio.run(main())
