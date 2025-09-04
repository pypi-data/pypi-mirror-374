from axiomtradeapi._client import AxiomTradeClient
from axiomtradeapi.auth.login import AxiomAuth

# Version
__version__ = "1.0.3"

# New client import (optional, token-based authentication)
try:
    from axiomtradeapi.client import AxiomTradeClient as TokenBasedClient, quick_login_and_get_trending, get_trending_with_token
    _has_token_client = True
except ImportError:
    TokenBasedClient = None
    quick_login_and_get_trending = None
    get_trending_with_token = None
    _has_token_client = False

__all__ = ['AxiomTradeClient', 'AxiomAuth', '__version__']

if _has_token_client:
    __all__.extend(['TokenBasedClient', 'quick_login_and_get_trending', 'get_trending_with_token'])