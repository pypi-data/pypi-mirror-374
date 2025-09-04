#!/usr/bin/env python3
"""
Test script for Axiom Trade API login functionality
Updated to test the new token-based authentication
"""

from axiomtradeapi import AxiomTradeClient
import json

def test_client_creation():
    """Test that the client can be created with tokens"""
    print("Testing client creation...")
    
    try:
        # Test with dummy tokens (since _client.py requires authentication)
        client = AxiomTradeClient(auth_token="dummy_token", refresh_token="dummy_refresh")
        
        # Check if required methods exist
        assert hasattr(client, 'set_tokens'), "set_tokens method missing"
        assert hasattr(client, 'get_tokens'), "get_tokens method missing"
        assert hasattr(client, 'is_authenticated'), "is_authenticated method missing"
        assert hasattr(client, 'subscribe_new_tokens'), "subscribe_new_tokens method missing"
        
        print("✓ Client created successfully with all required methods")
        return True
        
    except Exception as e:
        print(f"✗ Client creation failed: {e}")
        return False

def test_method_signatures():
    """Test that methods have correct signatures"""
    print("Testing method signatures...")
    
    try:
        client = AxiomTradeClient(auth_token="dummy_token", refresh_token="dummy_refresh")
        
        # Test method signatures by inspecting them
        import inspect
        
        # Check set_tokens method signature
        set_tokens_sig = inspect.signature(client.set_tokens)
        assert 'access_token' in set_tokens_sig.parameters, "set_tokens missing access_token parameter"
        assert 'refresh_token' in set_tokens_sig.parameters, "set_tokens missing refresh_token parameter"
        
        # Check subscribe_new_tokens signature  
        subscribe_sig = inspect.signature(client.subscribe_new_tokens)
        assert 'callback' in subscribe_sig.parameters, "subscribe_new_tokens missing callback parameter"
        
        print("✓ All method signatures are correct")
        return True
        
    except Exception as e:
        print(f"✗ Method signature test failed: {e}")
        return False
        
        # Check get_trending_tokens signature  
        trending_sig = inspect.signature(client.get_trending_tokens)
        assert 'time_period' in trending_sig.parameters, "get_trending_tokens missing time_period parameter"
        
        print("✓ All method signatures are correct")
        return True
        
    except Exception as e:
        print(f"✗ Method signature test failed: {e}")
        return False

def test_token_management():
    """Test token management functionality"""
    print("Testing token management...")
    
    try:
        client = AxiomTradeClient(auth_token="test_access_token", refresh_token="test_refresh_token")
        
        # Test initial state
        assert client.is_authenticated(), "Client should be authenticated with provided tokens"
        
        # Test getting tokens
        tokens = client.get_tokens()
        assert tokens['access_token'] == "test_access_token", "Access token not retrieved correctly"
        assert tokens['refresh_token'] == "test_refresh_token", "Refresh token not retrieved correctly"
        
        # Test setting new tokens
        client.set_tokens(access_token="new_access_token", refresh_token="new_refresh_token")
        updated_tokens = client.get_tokens()
        assert updated_tokens['access_token'] == "new_access_token", "Access token not updated correctly"
        assert updated_tokens['refresh_token'] == "new_refresh_token", "Refresh token not updated correctly"
        
        print("✓ Token management works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Token management test failed: {e}")
        return False

def main():
    print("Axiom Trade API - Login Integration Test")
    print("=" * 45)
    
    tests = [
        test_client_creation,
        test_method_signatures,
        test_token_management
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! Token-based authentication with _client.py is ready to use.")
        print("\nUsage examples:")
        print("1. Run 'python test.py' to test WebSocket with tokens from .env")
        print("2. Use: client = AxiomTradeClient(auth_token='...', refresh_token='...')")
        print("3. See AUTHENTICATION_CHANGES.md for detailed documentation")
    else:
        print("✗ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
