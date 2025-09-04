import requests
import json
import base64
import logging
from typing import Dict, Optional, List, Union
from .auth.auth_manager import AuthManager, create_authenticated_session
from .content.endpoints import Endpoints

# Trading-related imports
try:
    from solders.keypair import Keypair
    from solders.transaction import Transaction
    from solders.pubkey import Pubkey
    SOLDERS_AVAILABLE = True
except ImportError:
    SOLDERS_AVAILABLE = False

try:
    import base58
    BASE58_AVAILABLE = True
except ImportError:
    BASE58_AVAILABLE = False

class AxiomTradeClient:
    """
    Main client for interacting with Axiom Trade API with automatic token management
    """
    
    def __init__(self, username: str = None, password: str = None, 
                 auth_token: str = None, refresh_token: str = None,
                 storage_dir: str = None, use_saved_tokens: bool = True):
        """
        Initialize AxiomTradeClient with enhanced authentication
        
        Args:
            username: Email for automatic login
            password: Password for automatic login  
            auth_token: Existing auth token (optional)
            refresh_token: Existing refresh token (optional)
            storage_dir: Directory for secure token storage
            use_saved_tokens: Whether to load/save tokens automatically (default: True)
        """
        # Initialize the enhanced auth manager
        self.auth_manager = AuthManager(
            username=username,
            password=password,
            auth_token=auth_token,
            refresh_token=refresh_token,
            storage_dir=storage_dir,
            use_saved_tokens=use_saved_tokens
        )
        
        # Initialize endpoints for trading functionality
        self.endpoints = Endpoints()
        
        # Keep backward compatibility
        self.auth = self.auth_manager  # For legacy code
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://axiom.trade',
            'Connection': 'keep-alive',
            'Referer': 'https://axiom.trade/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site'
        }
    
    @property
    def access_token(self) -> Optional[str]:
        """Get current access token"""
        return self.auth_manager.tokens.access_token if self.auth_manager.tokens else None
    
    @property
    def refresh_token(self) -> Optional[str]:
        """Get current refresh token"""
        return self.auth_manager.tokens.refresh_token if self.auth_manager.tokens else None
    
    def login(self, email: str = None, password: str = None) -> Dict:
        """
        Login with username and password using the enhanced auth flow
        
        Args:
            email: Email address (optional if provided in constructor)
            password: Password (optional if provided in constructor)
            
        Returns:
            Dict: Login result with token information
        """
        # Use provided credentials or fall back to constructor values
        email = email or self.auth_manager.username
        password = password or self.auth_manager.password
        
        if not email or not password:
            raise ValueError("Email and password are required for login")
        
        # Update auth manager credentials
        self.auth_manager.username = email
        self.auth_manager.password = password
        
        # Perform authentication
        success = self.auth_manager.authenticate()
        
        if success and self.auth_manager.tokens:
            return {
                'success': True,
                'access_token': self.auth_manager.tokens.access_token,
                'refresh_token': self.auth_manager.tokens.refresh_token,
                'expires_at': self.auth_manager.tokens.expires_at,
                'message': 'Login successful'
            }
        else:
            return {
                'success': False,
                'message': 'Login failed'
            }
        
        return login_result
    
    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        """
        Set authentication tokens directly
        
        Args:
            access_token: The access token
            refresh_token: The refresh token
        """
        self.auth_manager._set_tokens(access_token, refresh_token)
    
    def get_tokens(self) -> Dict[str, Optional[str]]:
        """
        Get current tokens
        """
        tokens = self.auth_manager.tokens
        return {
            'access_token': tokens.access_token if tokens else None,
            'refresh_token': tokens.refresh_token if tokens else None,
            'expires_at': tokens.expires_at if tokens else None,
            'is_expired': tokens.is_expired if tokens else True
        }
    
    def is_authenticated(self) -> bool:
        """
        Check if the client has valid authentication tokens
        """
        return self.auth_manager.is_authenticated()
    
    def refresh_access_token(self) -> bool:
        """
        Refresh the access token using stored refresh token
        
        Returns:
            bool: True if refresh was successful, False otherwise
        """
        return self.auth_manager.refresh_tokens()
    
    def ensure_authenticated(self) -> bool:
        """
        Ensure the client has valid authentication tokens
        Automatically refreshes or re-authenticates as needed
        
        Returns:
            bool: True if valid authentication available, False otherwise
        """
        return self.auth_manager.ensure_valid_authentication()
    
    def logout(self) -> None:
        """Clear all authentication data including saved tokens"""
        self.auth_manager.logout()
    
    def clear_saved_tokens(self) -> bool:
        """Clear saved tokens from secure storage"""
        return self.auth_manager.clear_saved_tokens()
    
    def has_saved_tokens(self) -> bool:
        """Check if saved tokens exist in secure storage"""
        return self.auth_manager.has_saved_tokens()
    
    def get_token_info_detailed(self) -> Dict:
        """Get detailed information about current tokens"""
        return self.auth_manager.get_token_info()
    
    def get_trending_tokens(self, time_period: str = '1h') -> Dict:
        """
        Get trending meme tokens
        Available time periods: 1h, 24h, 7d
        """
        # Ensure we have valid authentication
        if not self.ensure_authenticated():
            raise ValueError("Authentication failed. Please login first.")
        
        url = f'https://api6.axiom.trade/meme-trending?timePeriod={time_period}'
        
        try:
            response = self.auth_manager.make_authenticated_request('GET', url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get trending tokens: {e}")
    
    def get_token_info(self, token_address: str) -> Dict:
        """
        Get information about a specific token
        """
        # Ensure we have valid authentication
        if not self.ensure_authenticated():
            raise ValueError("Authentication failed. Please login first.")
        
        # This endpoint might need to be confirmed with actual API documentation
        url = f'https://api6.axiom.trade/token/{token_address}'
        
        try:
            response = self.auth_manager.make_authenticated_request('GET', url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get token info: {e}")
    
    def get_user_portfolio(self) -> Dict:
        """
        Get user's portfolio information
        """
        # Ensure we have valid authentication
        if not self.ensure_authenticated():
            raise ValueError("Authentication failed. Please login first.")
        
        url = 'https://api6.axiom.trade/portfolio'
        
        try:
            response = self.auth_manager.make_authenticated_request('GET', url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get portfolio: {e}")
    
    def get_token_info_by_pair(self, pair_address: str) -> Dict:
        """
        Get token information by pair address
        
        Args:
            pair_address (str): The pair address to get info for
            
        Returns:
            Dict: Token information
        """
        # Ensure we have valid authentication
        if not self.ensure_authenticated():
            raise ValueError("Authentication failed. Please login first.")
        
        url = f'https://api10.axiom.trade/token-info?pairAddress={pair_address}'
        
        try:
            response = self.auth_manager.make_authenticated_request('GET', url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get token info: {e}")
    
    def get_last_transaction(self, pair_address: str) -> Dict:
        """
        Get last transaction for a pair
        
        Args:
            pair_address (str): The pair address to get last transaction for
            
        Returns:
            Dict: Last transaction information
        """
        # Ensure we have valid authentication
        if not self.ensure_authenticated():
            raise ValueError("Authentication failed. Please login first.")
        
        url = f'https://api10.axiom.trade/last-transaction?pairAddress={pair_address}'
        
        try:
            response = self.auth_manager.make_authenticated_request('GET', url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get last transaction: {e}")
    
    def get_pair_info(self, pair_address: str) -> Dict:
        """
        Get pair information
        
        Args:
            pair_address (str): The pair address to get info for
            
        Returns:
            Dict: Pair information
        """
        # Ensure we have valid authentication
        if not self.ensure_authenticated():
            raise ValueError("Authentication failed. Please login first.")
        
        url = f'https://api10.axiom.trade/pair-info?pairAddress={pair_address}'
        
        try:
            response = self.auth_manager.make_authenticated_request('GET', url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get pair info: {e}")
    
    def get_pair_stats(self, pair_address: str) -> Dict:
        """
        Get pair statistics
        
        Args:
            pair_address (str): The pair address to get stats for
            
        Returns:
            Dict: Pair statistics
        """
        # Ensure we have valid authentication
        if not self.ensure_authenticated():
            raise ValueError("Authentication failed. Please login first.")
        
        url = f'https://api10.axiom.trade/pair-stats?pairAddress={pair_address}'
        
        try:
            response = self.auth_manager.make_authenticated_request('GET', url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get pair stats: {e}")
    
    def get_meme_open_positions(self, wallet_address: str) -> Dict:
        """
        Get open meme token positions for a wallet
        
        Args:
            wallet_address (str): The wallet address to get positions for
            
        Returns:
            Dict: Open positions information
        """
        # Ensure we have valid authentication
        if not self.ensure_authenticated():
            raise ValueError("Authentication failed. Please login first.")
        
        url = f'https://api10.axiom.trade/meme-open-positions?walletAddress={wallet_address}'
        
        try:
            response = self.auth_manager.make_authenticated_request('GET', url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get open positions: {e}")
    
    def get_holder_data(self, pair_address: str, only_tracked_wallets: bool = False) -> Dict:
        """
        Get holder data for a pair
        
        Args:
            pair_address (str): The pair address to get holder data for
            only_tracked_wallets (bool): Whether to only include tracked wallets
            
        Returns:
            Dict: Holder data information
        """
        # Ensure we have valid authentication
        if not self.ensure_authenticated():
            raise ValueError("Authentication failed. Please login first.")
        
        url = f'https://api10.axiom.trade/holder-data-v3?pairAddress={pair_address}&onlyTrackedWallets={str(only_tracked_wallets).lower()}'
        
        try:
            response = self.auth_manager.make_authenticated_request('GET', url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get holder data: {e}")
    
    def get_dev_tokens(self, dev_address: str) -> Dict:
        """
        Get tokens created by a developer address
        
        Args:
            dev_address (str): The developer address to get tokens for
            
        Returns:
            Dict: Developer tokens information
        """
        # Ensure we have valid authentication
        if not self.ensure_authenticated():
            raise ValueError("Authentication failed. Please login first.")
        
        url = f'https://api10.axiom.trade/dev-tokens-v2?devAddress={dev_address}'
        
        try:
            response = self.auth_manager.make_authenticated_request('GET', url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get dev tokens: {e}")
    
    def get_token_analysis(self, dev_address: str, token_ticker: str) -> Dict:
        """
        Get token analysis for a developer and token ticker
        
        Args:
            dev_address (str): The developer address
            token_ticker (str): The token ticker to analyze
            
        Returns:
            Dict: Token analysis information
        """
        # Ensure we have valid authentication
        if not self.ensure_authenticated():
            raise ValueError("Authentication failed. Please login first.")
        
        url = f'https://api10.axiom.trade/token-analysis?devAddress={dev_address}&tokenTicker={token_ticker}'
        
        try:
            response = self.auth_manager.make_authenticated_request('GET', url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to get token analysis: {e}")
    
    # ==================== TRADING METHODS ====================
    
    def buy_token(self, private_key: str, token_mint: str, amount_sol: float, 
                  slippage_percent: float = 5.0) -> Dict[str, Union[str, bool]]:
        """
        Buy a token using SOL by building and sending Solana transactions directly.
        
        NOTE: This is a simplified implementation. Real DEX trading requires:
        - Token account management
        - Liquidity pool discovery
        - Price calculation with slippage
        - Complex instruction building for AMM protocols
        
        Args:
            private_key (str): Private key as base58 string or hex
            token_mint (str): Token mint address to buy
            amount_sol (float): Amount of SOL to spend
            slippage_percent (float): Slippage tolerance percentage (default: 5%)
            
        Returns:
            Dict with transaction signature and success status
        """
        if not SOLDERS_AVAILABLE:
            return {
                "success": False, 
                "error": "solders library not installed. Run: pip install solders"
            }
        
        try:
            # Convert private key to Keypair
            keypair = self._get_keypair_from_private_key(private_key)
            
            self.logger.info(f"Building buy transaction for {amount_sol} SOL worth of token {token_mint}")
            
            # This is where we would need to build a complete DEX transaction
            # For now, return a placeholder indicating manual implementation needed
            return {
                "success": False,
                "error": "Manual DEX transaction building required. This involves:\n" +
                       "1. Getting token account addresses\n" +
                       "2. Finding liquidity pools (Raydium, Orca, etc.)\n" +
                       "3. Calculating swap amounts with slippage\n" +
                       "4. Building complex transaction instructions\n" +
                       "5. Sending to RPC endpoint like: https://greer-651y13-fast-mainnet.helius-rpc.com/\n" +
                       "\nThis requires extensive Solana DEX integration beyond basic API calls."
            }
            
        except Exception as e:
            error_msg = f"Error in buy_token: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def sell_token(self, private_key: str, token_mint: str, amount_tokens: float, 
                   slippage_percent: float = 5.0) -> Dict[str, Union[str, bool]]:
        """
        Sell a token for SOL by building and sending Solana transactions directly.
        
        NOTE: This is a simplified implementation. Real DEX trading requires:
        - Token account management
        - Liquidity pool discovery
        - Price calculation with slippage
        - Complex instruction building for AMM protocols
        
        Args:
            private_key (str): Private key as base58 string or hex
            token_mint (str): Token mint address to sell
            amount_tokens (float): Amount of tokens to sell
            slippage_percent (float): Slippage tolerance percentage (default: 5%)
            
        Returns:
            Dict with transaction signature and success status
        """
        if not SOLDERS_AVAILABLE:
            return {
                "success": False, 
                "error": "solders library not installed. Run: pip install solders"
            }
        
        try:
            # Convert private key to Keypair
            keypair = self._get_keypair_from_private_key(private_key)
            
            self.logger.info(f"Building sell transaction for {amount_tokens} tokens of {token_mint}")
            
            # This is where we would need to build a complete DEX transaction
            # For now, return a placeholder indicating manual implementation needed
            return {
                "success": False,
                "error": "Manual DEX transaction building required. This involves:\n" +
                       "1. Getting token account addresses\n" +
                       "2. Finding liquidity pools (Raydium, Orca, etc.)\n" +
                       "3. Calculating swap amounts with slippage\n" +
                       "4. Building complex transaction instructions\n" +
                       "5. Sending to RPC endpoint like: https://greer-651y13-fast-mainnet.helius-rpc.com/\n" +
                       "\nThis requires extensive Solana DEX integration beyond basic API calls."
            }
            
        except Exception as e:
            error_msg = f"Error in sell_token: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def get_token_balance(self, wallet_address: str, token_mint: str) -> Optional[float]:
        """
        Get the balance of a specific token for a wallet.
        
        Args:
            wallet_address (str): Wallet public key
            token_mint (str): Token mint address
            
        Returns:
            Token balance as float, or None if error
        """
        try:
            # Ensure we have valid authentication
            if not self.ensure_authenticated():
                raise ValueError("Authentication failed")
            
            payload = {
                "publicKey": wallet_address,
                "tokenMint": token_mint
            }
            
            url = f"{self.endpoints.BASE_URL_API}{self.endpoints.ENDPOINT_GET_TOKEN_BALANCE}"
            response = self.auth_manager.make_authenticated_request('POST', url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                balance = result.get("balance", 0)
                self.logger.info(f"Token balance for {token_mint}: {balance}")
                return float(balance)
            else:
                self.logger.error(f"Failed to get token balance: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting token balance: {str(e)}")
            return None
    
    def get_sol_balance(self, wallet_address: str) -> Optional[float]:
        """
        Get SOL balance for a wallet address.
        
        Args:
            wallet_address (str): Wallet public key
            
        Returns:
            SOL balance as float, or None if error
        """
        try:
            # Ensure we have valid authentication
            if not self.ensure_authenticated():
                raise ValueError("Authentication failed")
            
            payload = {"publicKey": wallet_address}
            
            url = f"{self.endpoints.BASE_URL_API}{self.endpoints.ENDPOINT_GET_BALANCE}"
            response = self.auth_manager.make_authenticated_request('POST', url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                balance = result.get("balance", 0)
                self.logger.info(f"SOL balance for {wallet_address}: {balance}")
                return float(balance)
            else:
                self.logger.error(f"Failed to get SOL balance: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting SOL balance: {str(e)}")
            return None
    
    def send_transaction_to_rpc(self, signed_transaction_base64: str, 
                               rpc_url: str = "https://greer-651y13-fast-mainnet.helius-rpc.com/") -> Dict[str, Union[str, bool]]:
        """
        Send a signed transaction directly to Solana RPC endpoint.
        
        Args:
            signed_transaction_base64 (str): Base64 encoded signed transaction
            rpc_url (str): Solana RPC endpoint URL
            
        Returns:
            Dict with transaction signature and success status
        """
        try:
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en-US,en;q=0.9,es;q=0.8,fr;q=0.7,de;q=0.6,ru;q=0.5',
                'content-type': 'application/json',
                'origin': 'https://axiom.trade',
                'priority': 'u=1, i',
                'referer': 'https://axiom.trade/',
                'sec-ch-ua': '"Opera GX";v="120", "Not-A.Brand";v="8", "Chromium";v="135"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0'
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendTransaction",
                "params": [
                    signed_transaction_base64,
                    {
                        "encoding": "base64",
                        "skipPreflight": True,
                        "preflightCommitment": "confirmed",
                        "maxRetries": 0
                    }
                ]
            }
            
            self.logger.info(f"Sending transaction to RPC: {rpc_url}")
            
            response = requests.post(rpc_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    signature = result["result"]
                    self.logger.info(f"Transaction sent successfully. Signature: {signature}")
                    return {
                        "success": True,
                        "signature": signature,
                        "transactionId": signature
                    }
                elif "error" in result:
                    error_msg = f"RPC Error: {result['error']}"
                    self.logger.error(error_msg)
                    return {"success": False, "error": error_msg}
                else:
                    error_msg = f"Unexpected RPC response: {result}"
                    self.logger.error(error_msg)
                    return {"success": False, "error": error_msg}
            else:
                error_msg = f"Failed to send transaction: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error sending transaction to RPC: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _get_keypair_from_private_key(self, private_key: str) -> Keypair:
        """Convert private key string to Keypair object."""
        if not SOLDERS_AVAILABLE:
            raise ImportError("solders library not installed. Run: pip install solders")
        
        try:
            if isinstance(private_key, str):
                # Try to decode as base58 first
                try:
                    if BASE58_AVAILABLE:
                        import base58
                        private_key_bytes = base58.b58decode(private_key)
                    else:
                        # Fallback to assuming it's hex
                        private_key_bytes = bytes.fromhex(private_key)
                except:
                    # Try as hex string
                    try:
                        private_key_bytes = bytes.fromhex(private_key)
                    except:
                        # Try as base64
                        try:
                            private_key_bytes = base64.b64decode(private_key)
                        except:
                            raise ValueError("Unable to decode private key")
            else:
                private_key_bytes = private_key
            
            return Keypair.from_bytes(private_key_bytes)
        except Exception as e:
            raise ValueError(f"Invalid private key format: {e}")
    
    def _sign_and_send_transaction(self, keypair: Keypair, transaction_data: Dict) -> Dict[str, Union[str, bool]]:
        """Sign and send a transaction to the Solana network."""
        if not SOLDERS_AVAILABLE:
            return {
                "success": False, 
                "error": "solders library not installed. Run: pip install solders"
            }
        
        try:
            # Extract transaction from response
            if "transaction" in transaction_data:
                transaction_b64 = transaction_data["transaction"]
            elif "serializedTransaction" in transaction_data:
                transaction_b64 = transaction_data["serializedTransaction"]
            else:
                raise ValueError("No transaction found in API response")
            
            # Decode and deserialize transaction
            transaction_bytes = base64.b64decode(transaction_b64)
            transaction = Transaction.from_bytes(transaction_bytes)
            
            # Sign the transaction
            signed_transaction = transaction
            signed_transaction.sign([keypair])
            
            # Send the signed transaction back to API
            send_data = {
                "signedTransaction": base64.b64encode(bytes(signed_transaction)).decode('utf-8')
            }
            
            url = f"{self.endpoints.BASE_URL_API}{self.endpoints.ENDPOINT_SEND_TRANSACTION}"
            response = self.auth_manager.make_authenticated_request('POST', url, json=send_data)
            
            if response.status_code == 200:
                result = response.json()
                signature = result.get("signature", "")
                self.logger.info(f"Transaction sent successfully. Signature: {signature}")
                return {
                    "success": True,
                    "signature": signature,
                    "transactionId": signature
                }
            else:
                error_msg = f"Failed to send transaction: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error signing/sending transaction: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}

# Convenience functions for quick usage
def quick_login_and_get_trending(email: str, b64_password: str, otp_code: str, time_period: str = '1h') -> Dict:
    """
    Quick function to login and get trending tokens in one call
    """
    client = AxiomTradeClient()
    client.login(email, b64_password, otp_code)
    return client.get_trending_tokens(time_period)

def get_trending_with_token(access_token: str, time_period: str = '1h') -> Dict:
    """
    Quick function to get trending tokens with existing access token
    """
    client = AxiomTradeClient()
    client.set_tokens(access_token=access_token)
    return client.get_trending_tokens(time_period)
