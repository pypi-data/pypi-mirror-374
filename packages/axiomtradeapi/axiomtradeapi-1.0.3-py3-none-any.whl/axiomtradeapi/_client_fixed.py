from axiomtradeapi.content.endpoints import Endpoints
from axiomtradeapi.helpers.help import Helping
from axiomtradeapi.websocket._client import AxiomTradeWebSocketClient
from axiomtradeapi.auth import AuthManager
import requests
import logging
import json
from typing import List, Dict, Union, Optional
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price
from solders.pubkey import Pubkey
from solders.rpc.responses import SendTransactionResp
import base64
import time

class AxiomTradeClient:
    def __init__(self, username: str = None, password: str = None,
                 auth_token: str = None, refresh_token: str = None, 
                 log_level: int = logging.INFO) -> None:
        """
        Initialize Axiom Trade Client with automatic authentication
        
        Args:
            username: Email for automatic login (recommended)
            password: Password for automatic login (recommended)  
            auth_token: Existing auth token (optional)
            refresh_token: Existing refresh token (optional)
            log_level: Logging level
        """
        self.endpoints = Endpoints()
        self.base_url_api = self.endpoints.BASE_URL_API
        self.helper = Helping()
        
        # Initialize authentication manager
        self.auth_manager = AuthManager(
            username=username,
            password=password,
            auth_token=auth_token,
            refresh_token=refresh_token
        )
        
        # Setup logging
        self.logger = logging.getLogger("AxiomTradeAPI")
        self.logger.setLevel(log_level)
        
        # Create console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(log_level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Initialize WebSocket client with tokens from auth manager
        tokens = self.auth_manager.get_tokens()
        self.ws = AxiomTradeWebSocketClient(
            auth_token=tokens.access_token if tokens else auth_token,
            refresh_token=tokens.refresh_token if tokens else refresh_token,
            log_level=log_level
        )
            
    async def GetTokenPrice(self, token_symbol: str) -> Optional[float]:
        """Get the current price of a token by its symbol."""
        try:
            await self.ws.connect(is_token_price=True)
            token_subscribe = await self.ws.subscribe_token_price(token_symbol, lambda data: data.get("price"))
            if not token_subscribe:
                self.logger.error(f"Failed to subscribe to token price for {token_symbol}")
                return None
            self.logger.debug(f"Subscribed to token price for {token_symbol}")
            return token_subscribe
                
        except requests.exceptions.RequestException as err:
            error_msg = f"An error occurred: {err}"
            self.logger.error(error_msg)
            return None
            
    def GetBalance(self, wallet_address: str) -> Dict[str, Union[float, int]]:
        """Get balance for a single wallet address."""
        return self.GetBatchedBalance([wallet_address])[wallet_address]
            
    def GetBatchedBalance(self, wallet_addresses: List[str]) -> Dict[str, Dict[str, Union[float, int]]]:
        """Get balances for multiple wallet addresses in a single request."""
        try:
            payload = {
                "publicKeys": wallet_addresses
            }
            
            self.logger.debug(f"Sending batched balance request for wallets: {wallet_addresses}")
            self.logger.debug(f"Request payload: {json.dumps(payload)}")
            url = f"{self.base_url_api}{self.endpoints.ENDPOINT_GET_BATCHED_BALANCE}"
            self.logger.debug(f"Request URL: {url}")
            
            # Use authenticated session
            response = self.auth_manager.make_authenticated_request('POST', url, json=payload)
            self.logger.debug(f"Response status code: {response.status_code}")

            if response.status_code == 200:
                response_data = response.json()
                self.logger.debug(f"Response data: {json.dumps(response_data)}")
                
                result = {}
                for address in wallet_addresses:
                    if address in response_data:
                        balance_data = response_data[address]
                        sol = balance_data["solBalance"]
                        lamports = int(sol * 1_000_000_000)  # Convert SOL back to lamports
                        
                        result[address] = {
                            "sol": sol,
                            "lamports": lamports,
                            "slot": balance_data["slot"]
                        }
                        self.logger.info(f"Successfully retrieved balance for {address}: {sol} SOL")
                    else:
                        self.logger.warning(f"No balance data received for address: {address}")
                        result[address] = None
                
                return result
            else:
                error_msg = f"Error: {response.status_code}"
                self.logger.error(error_msg)
                return {addr: None for addr in wallet_addresses}
                
        except requests.exceptions.RequestException as err:
            error_msg = f"An error occurred: {err}"
            self.logger.error(error_msg)
            return {addr: None for addr in wallet_addresses}
    
    def buy_token(self, private_key: str, token_mint: str, amount_sol: float, 
                  slippage_percent: float = 5.0) -> Dict[str, Union[str, bool]]:
        """
        Buy a token using SOL.
        
        Args:
            private_key (str): Private key as base58 string or bytes
            token_mint (str): Token mint address to buy
            amount_sol (float): Amount of SOL to spend
            slippage_percent (float): Slippage tolerance percentage (default: 5%)
            
        Returns:
            Dict with transaction signature and success status
        """
        try:
            # Convert private key to Keypair
            keypair = self._get_keypair_from_private_key(private_key)
            
            # Prepare buy transaction data
            buy_data = {
                "user": str(keypair.pubkey()),
                "tokenMint": token_mint,
                "amountSol": amount_sol,
                "slippagePercent": slippage_percent,
                "computeUnits": 200000,
                "computeUnitPrice": 1000000
            }
            
            self.logger.info(f"Initiating buy order for {amount_sol} SOL worth of token {token_mint}")
            
            # Get transaction from API
            url = f"{self.base_url_api}{self.endpoints.ENDPOINT_BUY_TOKEN}"
            response = self.auth_manager.make_authenticated_request('POST', url, json=buy_data)
            
            if response.status_code != 200:
                error_msg = f"Failed to get buy transaction: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            transaction_data = response.json()
            
            # Sign and send transaction
            return self._sign_and_send_transaction(keypair, transaction_data)
            
        except Exception as e:
            error_msg = f"Error in buy_token: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def sell_token(self, private_key: str, token_mint: str, amount_tokens: float, 
                   slippage_percent: float = 5.0) -> Dict[str, Union[str, bool]]:
        """
        Sell a token for SOL.
        
        Args:
            private_key (str): Private key as base58 string or bytes
            token_mint (str): Token mint address to sell
            amount_tokens (float): Amount of tokens to sell
            slippage_percent (float): Slippage tolerance percentage (default: 5%)
            
        Returns:
            Dict with transaction signature and success status
        """
        try:
            # Convert private key to Keypair
            keypair = self._get_keypair_from_private_key(private_key)
            
            # Prepare sell transaction data
            sell_data = {
                "user": str(keypair.pubkey()),
                "tokenMint": token_mint,
                "amountTokens": amount_tokens,
                "slippagePercent": slippage_percent,
                "computeUnits": 200000,
                "computeUnitPrice": 1000000
            }
            
            self.logger.info(f"Initiating sell order for {amount_tokens} tokens of {token_mint}")
            
            # Get transaction from API
            url = f"{self.base_url_api}{self.endpoints.ENDPOINT_SELL_TOKEN}"
            response = self.auth_manager.make_authenticated_request('POST', url, json=sell_data)
            
            if response.status_code != 200:
                error_msg = f"Failed to get sell transaction: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            transaction_data = response.json()
            
            # Sign and send transaction
            return self._sign_and_send_transaction(keypair, transaction_data)
            
        except Exception as e:
            error_msg = f"Error in sell_token: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _get_keypair_from_private_key(self, private_key: str) -> Keypair:
        """Convert private key string to Keypair object."""
        try:
            if isinstance(private_key, str):
                # Try to decode as base58 first
                try:
                    from base58 import b58decode
                    private_key_bytes = b58decode(private_key)
                except ImportError:
                    # Fallback to manual base58 decoding or assume it's already bytes
                    import base64
                    try:
                        private_key_bytes = base64.b64decode(private_key)
                    except:
                        # Assume it's a hex string
                        private_key_bytes = bytes.fromhex(private_key)
                except:
                    # Assume it's a hex string
                    private_key_bytes = bytes.fromhex(private_key)
            else:
                private_key_bytes = private_key
            
            return Keypair.from_bytes(private_key_bytes)
        except Exception as e:
            raise ValueError(f"Invalid private key format: {e}")
    
    def _sign_and_send_transaction(self, keypair: Keypair, transaction_data: Dict) -> Dict[str, Union[str, bool]]:
        """Sign and send a transaction to the Solana network."""
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
            
            url = f"{self.base_url_api}{self.endpoints.ENDPOINT_SEND_TRANSACTION}"
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
            payload = {
                "publicKey": wallet_address,
                "tokenMint": token_mint
            }
            
            url = f"{self.base_url_api}{self.endpoints.ENDPOINT_GET_TOKEN_BALANCE}"
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

    async def subscribe_new_tokens(self, callback):
        """Subscribe to new token updates via WebSocket."""
        return await self.ws.subscribe_new_tokens(callback)
