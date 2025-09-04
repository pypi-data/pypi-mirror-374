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
import hashlib

from axiomtradeapi.urls import AAllBaseUrls, AxiomTradeApiUrls
from axiomtradeapi.helpers.TryServers import try_servers

class AxiomTradeClient:
    def __init__(self, username: str = None, password: str = None, 
                 auth_token: str = None, refresh_token: str = None,
                 log_level: int = logging.INFO) -> None:
        """
        Initialize Axiom Trade Client with automatic authentication
        
        Args:
            username: Email for automatic login (optional if tokens provided)
            password: Password for automatic login (optional if tokens provided)
            auth_token: Existing auth token (optional)
            refresh_token: Existing refresh token (optional)
            log_level: Logging level
        """
        self.endpoints = Endpoints()
        self.base_url_api = self.endpoints.BASE_URL_API
        self.helper = Helping()
        
        # Validate that either credentials or tokens are provided
        has_credentials = username and password
        has_tokens = auth_token and refresh_token
        
        if not has_credentials and not has_tokens:
            raise ValueError("Either username/password or auth_token/refresh_token must be provided")
        
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
        
        # Initialize WebSocket client with auth manager
        self.ws = AxiomTradeWebSocketClient(
            auth_manager=self.auth_manager,
            log_level=log_level
        )
    
    def set_tokens(self, access_token: str = None, refresh_token: str = None):
        """
        Set access and refresh tokens manually
        """
        if access_token or refresh_token:
            from axiomtradeapi.auth.auth_manager import AuthTokens
            # Update the auth manager's tokens
            if not self.auth_manager.tokens:
                self.auth_manager.tokens = AuthTokens(
                    access_token=access_token or "",
                    refresh_token=refresh_token or "",
                    expires_at=None
                )
            else:
                if access_token:
                    self.auth_manager.tokens.access_token = access_token
                if refresh_token:
                    self.auth_manager.tokens.refresh_token = refresh_token
    
    def get_tokens(self) -> Dict[str, Optional[str]]:
        """
        Get current tokens
        """
        if self.auth_manager.tokens:
            return {
                'access_token': self.auth_manager.tokens.access_token,
                'refresh_token': self.auth_manager.tokens.refresh_token
            }
        return {'access_token': None, 'refresh_token': None}
    
    def is_authenticated(self) -> bool:
        """
        Check if the client has valid authentication tokens
        """
        return self.auth_manager.tokens is not None and bool(self.auth_manager.tokens.access_token)
            
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
    
    def login_step1(self, email: str, b64_password: str) -> str:
        """
        First step of login - send email and password to get OTP JWT token
        Returns the OTP JWT token needed for step 2
        """
        url = f'{AAllBaseUrls.BASE_URL_v3}{AxiomTradeApiUrls.LOGIN_STEP1}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'Origin': 'https://axiom.trade',
            'Connection': 'keep-alive',
            'Referer': 'https://axiom.trade/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'TE': 'trailers'
        }
        
        data = {
            "email": email,
            "b64Password": b64_password
        }
        
        self.logger.debug(f"Sending login step 1 request for email: {email}")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        otp_token = result.get('otpJwtToken')
        self.logger.debug("OTP JWT token received successfully")
        return otp_token

    def login_step1_try_servers(self, email: str, b64_password: str, otp_token: str = "") -> str:
        """
        First step of login - tries all servers for login step 1, returns the OTP JWT token from the first server that responds with 200.
        The token is extracted from the response cookies (auth-otp-login-token).
        All headers are set as in the curl example, including the Cookie header.
        Args:
            email (str): User email
            b64_password (str): Base64-encoded password
            otp_token (str): Optional, value for auth-otp-login-token cookie (default: empty)
        """
        path = AxiomTradeApiUrls.LOGIN_STEP1
        data = {
            "email": email,
            "b64Password": b64_password
        }
        print(data)
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9,es;q=0.8',
            'content-type': 'application/json',
            'origin': 'https://axiom.trade',
            'priority': 'u=1, i',
            'referer': 'https://axiom.trade/',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Opera GX";v="119"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0',
            'Cookie': f'auth-otp-login-token={otp_token}'
        }
        self.logger.debug(f"Trying login step 1 on all servers for email: {email}")
        base_url = f'{AAllBaseUrls.BASE_URL_v6}{AxiomTradeApiUrls.LOGIN_STEP1}'
        if base_url is None:
            raise Exception("No server responded with 200 for login step 1.")
        response = requests.post(base_url, headers=headers, json=data)
        print(f"Response from server: {response.json()}")
        otp_token = response.cookies.get('auth-otp-login-token')
        if not otp_token:
            self.logger.error("auth-otp-login-token not found in cookies!")
            raise Exception("auth-otp-login-token not found in cookies!")
        self.logger.debug(f"OTP JWT token received from {base_url} (from cookies)")
        return otp_token

    def login_step2(self, otp_jwt_token: str, otp_code: str, email: str, b64_password: str) -> Dict:
        """
        Second step of login - send OTP code to complete authentication
        Returns client credentials (clientSecret, orgId, userId)
        """
        url = f'{AAllBaseUrls.BASE_URL_v3}{AxiomTradeApiUrls.LOGIN_STEP2}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'Origin': 'https://axiom.trade',
            'Connection': 'keep-alive',
            'Referer': 'https://axiom.trade/',
            'Cookie': f'auth-otp-login-token={otp_jwt_token}',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'TE': 'trailers'
        }
        
        data = {
            "code": otp_code,
            "email": email,
            "b64Password": b64_password
        }
        
        self.logger.debug("Sending login step 2 request with OTP code")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        credentials = response.json()
        self.logger.info("Login completed successfully")
        return credentials

    def get_b64_password(self, password: str) -> str:
        """
        Hash the password with SHA256 and then base64 encode the result, using ISO-8859-1 encoding for the password.
        """
        sha256_hash = hashlib.sha256(password.encode('iso-8859-1')).digest()
        b64_password = base64.b64encode(sha256_hash).decode('utf-8')
        return b64_password

    def complete_login(self, email: str, b64_password: str) -> Dict:
        """
        Complete the full login process
        Returns client credentials (clientSecret, orgId, userId)
        """
        self.logger.info("Starting login process...")
        #b64_password = self.get_b64_password(password)
        otp_jwt_token = self.login_step1_try_servers(email, b64_password)
        otp_code = input("Enter the OTP code sent to your email: ")
        credentials = self.login_step2(otp_jwt_token, otp_code, email, b64_password)
        
        # Store credentials in auth manager if available
        if hasattr(self, 'auth_manager'):
            # Update auth manager with new credentials
            # Note: This may need adjustment based on how auth_manager handles these credentials
            pass
            
        return credentials

    def refresh_access_token_direct(self, refresh_token: str) -> str:
        """
        Refresh the access token using a refresh token
        Returns the new access token
        """
        url = 'https://api9.axiom.trade/refresh-access-token'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Origin': 'https://axiom.trade',
            'Connection': 'keep-alive',
            'Referer': 'https://axiom.trade/',
            'Cookie': f'auth-refresh-token={refresh_token}',
            'Content-Length': '0',
            'TE': 'trailers'
        }
        
        self.logger.debug("Refreshing access token")
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        
        # Check if token is in response JSON or cookies
        try:
            result = response.json()
            new_token = result.get('auth-access-token')
        except:
            new_token = None
            
        if not new_token:
            # Try to get from cookies
            new_token = response.cookies.get('auth-access-token')
            
        if new_token:
            self.logger.debug("Access token refreshed successfully")
        else:
            self.logger.warning("Could not extract new access token from response")
            
        return new_token

    def get_trending_tokens(self, access_token: str, time_period: str = '1h') -> Dict:
        """
        Get trending meme tokens
        Available time periods: 1h, 24h, 7d
        """
        url = f'https://api6.axiom.trade/meme-trending?timePeriod={time_period}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Origin': 'https://axiom.trade',
            'Connection': 'keep-alive',
            'Referer': 'https://axiom.trade/',
            'Cookie': f'auth-access-token={access_token}',
            'TE': 'trailers'
        }
        
        self.logger.debug(f"Fetching trending tokens for period: {time_period}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        self.logger.debug(f"Retrieved {len(result) if isinstance(result, list) else 'N/A'} trending tokens")
        return result
