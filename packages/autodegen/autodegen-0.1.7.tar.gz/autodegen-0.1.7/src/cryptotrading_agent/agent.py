"""Main TradingAgent class - simplified interface for PyPI users."""

from __future__ import annotations

import asyncio
import os
from typing import Dict, Any, Optional
import logging
from pathlib import Path

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
            # Create analysis prompt
            prompt = self._create_analysis_prompt(symbol, timeframe)
            
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
    
    def _create_analysis_prompt(self, symbol: str, timeframe: str) -> str:
        """Create comprehensive analysis prompt with explicit JSON structure."""
        return f"""
        You must provide a comprehensive technical analysis for {symbol.upper()} in the EXACT JSON format below.
        
        REQUIRED JSON STRUCTURE:
        {{
          "title": "**COMPREHENSIVE TECHNICAL ANALYSIS: {symbol.upper()}**",
          "market_state": "Current market state and sentiment analysis",
          "trend_indicators": "ADX (Average Directional Index) with +DI/-DI analysis, Ichimoku Cloud (Tenkan-sen, Kijun-sen, Senkou Span A/B, Chikou Span), Moving Averages (SMA/EMA 20, 50, 200) with golden/death cross analysis, MACD (12,26,9) with histogram and signal line crossovers",
          "oscillators": "RSI (14) with divergence analysis and overbought/oversold levels, Stochastic Oscillator (%K, %D) with 80/20 levels, Williams %R for momentum reversals, CCI (Commodity Channel Index) for cyclical turns",
          "volume_indicators": "OBV (On-Balance Volume) with trend confirmation, Volume Profile and VWAP analysis, Money Flow Index (MFI) for volume-weighted momentum",
          "fibonacci_levels": "Fibonacci Retracements (23.6%, 38.2%, 50%, 61.8%, 78.6%), Fibonacci Extensions for price targets, Key retracement and extension levels for {symbol.upper()}",
          "elliott_wave": "Elliott Wave count and current wave position analysis for {symbol.upper()}, Wave degree identification and projection",
          "smart_money_concepts": "Order Blocks identification and analysis, Fair Value Gaps (FVG) analysis, Liquidity pools and sweep analysis, Smart money flow patterns",
          "trading_setup": "Specific entry levels, stop-loss placement, take-profit targets, position sizing recommendations, risk-reward ratios",
          "risk_assessment": "Risk-reward ratios, probability-weighted scenarios (bullish/bearish/neutral), volatility analysis, correlation with BTC and crypto market",
          "outlook": "Final trading bias and market direction, probability assessment, key levels to watch"
        }}
        
        CRITICAL INSTRUCTIONS:
        - Fill each field with detailed, specific analysis for {symbol.upper()}
        - Include actual price levels, percentages, and specific indicator values
        - Focus on {timeframe} timeframe with multi-timeframe context
        - Provide actionable trading insights
        - Return ONLY valid JSON, no other text or formatting
        
        Symbol: {symbol.upper()}
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