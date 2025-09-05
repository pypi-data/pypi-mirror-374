"""Main TradingAgent class - simplified interface for PyPI users."""

from __future__ import annotations

import asyncio
import os
from typing import Dict, Any, Optional
import logging
from pathlib import Path
import aiohttp
from datetime import datetime

# Import existing components
import sys
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from .core import LLMCore, ReportSchema
from .exceptions import TradingAgentError, APIError, ConfigurationError

logger = logging.getLogger(__name__)


class TradingAgent:
    """
    Production-ready crypto trading analysis agent.
    
    Features:
    - Real-time market analysis with technical indicators
    - Production-hardened LLM responses (no meta commentary)
    - Enterprise security patterns (circuit breaker, retry, firewall)
    - Support for major exchanges and DeFi protocols
    
    Example:
        >>> agent = TradingAgent()
        >>> analysis = await agent.analyze("BTC")
        >>> print(analysis.title)
        **COMPREHENSIVE TECHNICAL ANALYSIS: BTC**
    """
    
    def __init__(
        self,
        fireworks_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        binance_api_key: Optional[str] = None,
        binance_api_secret: Optional[str] = None,
        load_dotenv: bool = True
    ):
        """
        Initialize the trading agent.
        
        Args:
            fireworks_api_key: Fireworks AI API key (or set FIREWORKS_API_KEY env var)
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)  
            binance_api_key: Binance API key (or set BINANCE_API_KEY env var)
            binance_api_secret: Binance API secret (or set BINANCE_API_SECRET env var)
            load_dotenv: Whether to load environment variables from .env file
        """
        
        if load_dotenv:
            try:
                from dotenv import load_dotenv as _load_dotenv
                _load_dotenv()
            except ImportError:
                logger.warning("python-dotenv not available, skipping .env file loading")
        
        # Setup API keys
        self.fireworks_api_key = fireworks_api_key or os.getenv("FIREWORKS_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.binance_api_key = binance_api_key or os.getenv("BINANCE_API_KEY")
        self.binance_api_secret = binance_api_secret or os.getenv("BINANCE_API_SECRET")
        
        # Validate required keys
        if not self.fireworks_api_key:
            raise ConfigurationError(
                "Fireworks API key is required. Set FIREWORKS_API_KEY environment variable "
                "or pass fireworks_api_key parameter."
            )
        
        # Initialize core components
        try:
            self.llm_core = LLMCore(api_key=self.fireworks_api_key)
            logger.info("TradingAgent initialized with production hardening enabled")
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize LLM core: {e}") from e
    
    async def _fetch_market_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch real-time market data from Binance API."""
        try:
            base_url = "https://api.binance.com/api/v3"
            
            async with aiohttp.ClientSession() as session:
                # Get current price
                ticker_url = f"{base_url}/ticker/24hr?symbol={symbol}USDT"
                async with session.get(ticker_url) as response:
                    if response.status == 200:
                        ticker_data = await response.json()
                        
                        return {
                            "symbol": symbol,
                            "price": float(ticker_data["lastPrice"]),
                            "change_24h": float(ticker_data["priceChangePercent"]),
                            "volume_24h": float(ticker_data["volume"]),
                            "high_24h": float(ticker_data["highPrice"]),
                            "low_24h": float(ticker_data["lowPrice"]),
                            "timestamp": datetime.now().isoformat()
                        }
            
            # Fallback data if API fails
            return {
                "symbol": symbol,
                "price": 0.0,
                "change_24h": 0.0,
                "volume_24h": 0.0,
                "high_24h": 0.0,
                "low_24h": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": "Unable to fetch live market data"
            }
            
        except Exception as e:
            logger.warning(f"Failed to fetch market data for {symbol}: {e}")
            return {
                "symbol": symbol,
                "price": 0.0,
                "change_24h": 0.0,
                "volume_24h": 0.0,
                "high_24h": 0.0,
                "low_24h": 0.0,
                "timestamp": datetime.now().isoformat(),
                "error": f"Market data fetch failed: {e}"
            }
    
    async def analyze(
        self, 
        symbol: str, 
        timeframe: str = "1h",
        structured: bool = True,
        timeout: float = 30.0
    ) -> ReportSchema | str:
        """
        Analyze a cryptocurrency symbol and return trading insights.
        
        Args:
            symbol: Crypto symbol to analyze (e.g., "BTC", "ETH", "SOL")
            timeframe: Analysis timeframe ("1h", "4h", "1d")
            structured: Whether to enforce structured output schema
            timeout: Request timeout in seconds
            
        Returns:
            ReportSchema object with structured analysis or string if structured=False
            
        Raises:
            APIError: If external API calls fail
            TradingAgentError: If analysis generation fails
        """
        try:
            # Fetch real market data first
            logger.info(f"Fetching real-time market data for {symbol}...")
            market_data = await self._fetch_market_data(symbol)
            
            # Create analysis prompt with real data
            prompt = self._create_analysis_prompt(symbol, timeframe, market_data)
            
            # Generate structured analysis
            if structured:
                report, error = await self.llm_core.complete_structured(
                    messages=[{"role": "user", "content": prompt}],
                    timeout=timeout,
                    enforce_schema=True
                )
                
                if report is None:
                    raise TradingAgentError(f"Analysis generation failed: {error}")
                
                return report
            else:
                # Use fallback method for text output
                result = await self.llm_core.complete_with_fallback(
                    messages=[{"role": "user", "content": prompt}],
                    timeout=timeout
                )
                
                if result.startswith("**ANALYSIS UNAVAILABLE**"):
                    raise TradingAgentError("Analysis generation failed - system unavailable")
                
                return result
                
        except asyncio.TimeoutError as e:
            raise TradingAgentError(f"Analysis timed out after {timeout}s") from e
        except Exception as e:
            logger.error(f"Analysis failed for {symbol}: {e}")
            raise TradingAgentError(f"Failed to analyze {symbol}: {e}") from e
    
    def _create_analysis_prompt(self, symbol: str, timeframe: str, market_data: Dict[str, Any]) -> str:
        """Create comprehensive analysis prompt with real market data and explicit JSON structure."""
        
        # Format price data for prompt
        price_info = f"""
CURRENT MARKET DATA for {symbol.upper()}:
- Current Price: ${market_data['price']:,.2f}
- 24h Change: {market_data['change_24h']:+.2f}%
- 24h High: ${market_data['high_24h']:,.2f}
- 24h Low: ${market_data['low_24h']:,.2f}
- 24h Volume: {market_data['volume_24h']:,.0f}
- Data Timestamp: {market_data['timestamp']}
        """
        
        return f"""
        {price_info}
        
        You must provide a comprehensive technical analysis for {symbol.upper()} based on the CURRENT MARKET DATA above in the EXACT JSON format below.
        
        REQUIRED JSON STRUCTURE:
        {{
          "title": "**COMPREHENSIVE TECHNICAL ANALYSIS: {symbol.upper()}**",
          "market_state": "Current market state and sentiment analysis based on ${market_data['price']:,.2f} price level and {market_data['change_24h']:+.2f}% 24h change",
          "trend_indicators": "ADX analysis relative to ${market_data['price']:,.2f} current price, Ichimoku Cloud levels, Moving Averages (SMA/EMA 20, 50, 200) positions relative to current price, MACD analysis",
          "oscillators": "RSI (14) analysis at current ${market_data['price']:,.2f} level, Stochastic Oscillator analysis, Williams %R analysis, CCI analysis - ALL relative to current price",
          "volume_indicators": "OBV analysis with current volume {market_data['volume_24h']:,.0f}, Volume Profile analysis, VWAP relative to ${market_data['price']:,.2f}, MFI analysis",
          "fibonacci_levels": "Fibonacci Retracements calculated from recent high ${market_data['high_24h']:,.2f} to low ${market_data['low_24h']:,.2f}, key levels relative to current ${market_data['price']:,.2f}",
          "elliott_wave": "Elliott Wave analysis based on current price action at ${market_data['price']:,.2f}, wave count and projections",
          "smart_money_concepts": "Order Blocks, Fair Value Gaps, and liquidity analysis around current ${market_data['price']:,.2f} level",
          "trading_setup": "Entry levels relative to ${market_data['price']:,.2f}, stop-loss and take-profit calculations, position sizing based on current volatility",
          "risk_assessment": "Risk analysis based on current price ${market_data['price']:,.2f} and 24h volatility ({market_data['change_24h']:+.2f}%), probability scenarios",
          "outlook": "Trading bias based on current market data showing ${market_data['price']:,.2f} price with {market_data['change_24h']:+.2f}% daily change"
        }}
        
        CRITICAL INSTRUCTIONS:
        - Use the ACTUAL current price ${market_data['price']:,.2f} in ALL calculations and analysis
        - Base ALL technical levels on real market data provided above
        - Consider the 24h change of {market_data['change_24h']:+.2f}% in sentiment analysis
        - Use realistic price levels around the current ${market_data['price']:,.2f} price
        - Focus on {timeframe} timeframe analysis
        - Return ONLY valid JSON, no other text
        
        Symbol: {symbol.upper()}
        Current Price: ${market_data['price']:,.2f}
        Timeframe: {timeframe}
        """
    
    async def get_market_overview(self) -> str:
        """
        Get a general cryptocurrency market overview.
        
        Returns:
            Market overview analysis as formatted string
        """
        try:
            prompt = """
            Provide a comprehensive cryptocurrency market overview covering:
            - Overall market sentiment and direction
            - Key market drivers and catalysts
            - Major cryptocurrency performance (BTC, ETH, major altcoins)
            - Market risks and opportunities
            - DeFi and institutional adoption trends
            
            Keep the analysis professional and actionable for traders.
            """
            
            result = await self.llm_core.complete_with_fallback(
                messages=[{"role": "user", "content": prompt}],
                timeout=30.0
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Market overview failed: {e}")
            raise TradingAgentError(f"Failed to get market overview: {e}") from e
    
    def get_supported_symbols(self) -> list[str]:
        """
        Get list of supported cryptocurrency symbols.
        
        Returns:
            List of supported symbol strings
        """
        return [
            "BTC", "ETH", "BNB", "SOL", "ADA", "XRP", "DOT", "AVAX",
            "MATIC", "LINK", "UNI", "ATOM", "FTM", "NEAR", "ALGO",
            "VET", "ICP", "FLOW", "SAND", "MANA", "CRV", "COMP"
        ]
    
    async def health_check(self) -> dict[str, Any]:
        """
        Perform a health check of the trading agent components.
        
        Returns:
            Dictionary with health status of various components
        """
        health = {
            "status": "healthy",
            "components": {},
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Check LLM core
        try:
            if self.llm_core.circuit_breaker.can_proceed():
                health["components"]["llm_core"] = "operational"
            else:
                health["components"]["llm_core"] = "circuit_breaker_open"
                health["status"] = "degraded"
        except Exception as e:
            health["components"]["llm_core"] = f"error: {e}"
            health["status"] = "unhealthy"
        
        # Check API connectivity (placeholder - would test actual APIs)
        health["components"]["fireworks_api"] = "configured" if self.fireworks_api_key else "missing"
        health["components"]["binance_api"] = "configured" if self.binance_api_key else "missing"
        
        return health
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup resources if needed
        pass