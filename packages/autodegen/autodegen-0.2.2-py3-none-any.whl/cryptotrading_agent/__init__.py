"""
CryptoTrading Agent - Production-ready crypto trading analysis with LLM hardening.

A comprehensive cryptocurrency trading analysis agent that provides:
- Real-time market analysis with technical indicators
- Multi-expert AI coordination for trading insights  
- Production-hardened LLM responses with zero meta commentary
- Enterprise-grade security and resilience patterns
- Support for major crypto exchanges (Binance, DeFi protocols)

Example:
    >>> from cryptotrading_agent import TradingAgent
    >>> agent = TradingAgent()
    >>> analysis = await agent.analyze("BTC")
    >>> print(analysis.outlook)
"""

from __future__ import annotations

__version__ = "0.2.2"
__author__ = "Taygun Dogan"
__email__ = "taygundogan@example.com"
__license__ = "MIT"

# Core exports
from .agent import TradingAgent
from .cli import main as cli_main
from .core import LLMCore, ReportSchema
from .exceptions import TradingAgentError, APIError, ValidationError

__all__ = [
    # Main API
    "TradingAgent",
    "cli_main",
    
    # Core components
    "LLMCore", 
    "ReportSchema",
    
    # Exceptions
    "TradingAgentError",
    "APIError", 
    "ValidationError",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]

# Package info for introspection
def get_version() -> str:
    """Get the current package version."""
    return __version__

def get_info() -> dict[str, str]:
    """Get package information."""
    return {
        "name": "autodegen",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "description": "Production-ready crypto trading analysis agent with LLM hardening",
    }