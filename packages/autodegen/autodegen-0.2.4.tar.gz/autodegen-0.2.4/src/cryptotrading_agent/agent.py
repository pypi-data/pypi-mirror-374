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
from .technical_analyzer import TechnicalAnalyzer, TechnicalData

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
            self.technical_analyzer = TechnicalAnalyzer()
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
        timeout: float = 30.0,
        verbose: bool = True
    ) -> ReportSchema | str:
        """
        Analyze a cryptocurrency symbol and return trading insights.
        
        Args:
            symbol: Crypto symbol to analyze (e.g., "BTC", "ETH", "SOL")
            timeframe: Analysis timeframe ("1h", "4h", "1d")
            structured: Whether to enforce structured output schema
            timeout: Request timeout in seconds
            verbose: Whether to generate comprehensive analysis with all sections
            
        Returns:
            ReportSchema object with structured analysis or string if structured=False
            
        Raises:
            APIError: If external API calls fail
            TradingAgentError: If analysis generation fails
        """
        try:
            # Perform comprehensive technical analysis
            logger.info(f"Performing comprehensive technical analysis for {symbol} ({timeframe})...")
            
            async with self.technical_analyzer as analyzer:
                technical_data = await analyzer.analyze_symbol(symbol, timeframe)
                
            if technical_data is None:
                raise TradingAgentError(f"Failed to fetch technical data for {symbol}")
            
            # Create analysis prompt with real technical data
            prompt = self._create_analysis_prompt_with_technical_data(symbol, timeframe, technical_data, verbose=verbose)
            
            # Generate structured analysis
            if structured:
                report, error = await self.llm_core.complete_structured(
                    messages=[{"role": "user", "content": prompt}],
                    timeout=timeout,
                    enforce_schema=True,
                    verbose=verbose
                )
                
                if report is None:
                    raise TradingAgentError(f"Analysis generation failed: {error}")
                
                return report
            else:
                # Use fallback method for text output
                result = await self.llm_core.complete_with_fallback(
                    messages=[{"role": "user", "content": prompt}],
                    timeout=timeout,
                    verbose=verbose
                )
                
                if result.startswith("**ANALYSIS UNAVAILABLE**"):
                    raise TradingAgentError("Analysis generation failed - system unavailable")
                
                return result
                
        except asyncio.TimeoutError as e:
            raise TradingAgentError(f"Analysis timed out after {timeout}s") from e
        except Exception as e:
            logger.error(f"Analysis failed for {symbol}: {e}")
            raise TradingAgentError(f"Failed to analyze {symbol}: {e}") from e
    
    def _create_analysis_prompt_with_technical_data(self, symbol: str, timeframe: str, tech_data: TechnicalData, verbose: bool = True) -> str:
        """Create comprehensive analysis prompt with REAL calculated technical data."""
        
        # Format fibonacci levels properly
        fibonacci_text = " | ".join([f"{level}%: ${price:,.2f}" for level, price in tech_data.fibonacci_levels.items()]) if tech_data.fibonacci_levels else "Levels calculated from recent range"
        
        # Format support/resistance levels
        support_text = ' / '.join([f'${level:,.2f}' for level in tech_data.support_levels[:2]]) if tech_data.support_levels else 'N/A'
        resistance_text = ' / '.join([f'${level:,.2f}' for level in tech_data.resistance_levels[:2]]) if tech_data.resistance_levels else 'N/A'
        
        # Format risk level
        atr_text = f"{tech_data.atr:.2f}" if tech_data.atr else "N/A"
        risk_level = "HIGH" if tech_data.atr and tech_data.atr > tech_data.current_price * 0.05 else "MODERATE" if tech_data.atr and tech_data.atr > tech_data.current_price * 0.02 else "LOW"
        
        # Format outlook components
        trend_dir = tech_data.trend_direction.upper() if tech_data.trend_direction else "NEUTRAL"
        trend_str = tech_data.trend_strength if tech_data.trend_strength else "unknown"
        support_level = f"{tech_data.support_levels[0]:,.2f}" if tech_data.support_levels else "N/A"
        resistance_level = f"{tech_data.resistance_levels[0]:,.2f}" if tech_data.resistance_levels else "N/A"
        
        # Format comprehensive technical data for prompt
        technical_info = f"""
REAL-TIME TECHNICAL ANALYSIS DATA for {symbol.upper()} ({timeframe}):

PRICE DATA:
- Current Price: ${tech_data.current_price:,.2f}
- 24h Change: {tech_data.price_change_24h:+.2f}%
- 24h High: ${tech_data.high_24h:,.2f}
- 24h Low: ${tech_data.low_24h:,.2f}
- 24h Volume: {tech_data.volume_24h:,.0f}

REAL CALCULATED INDICATORS:
- RSI (14): {tech_data.rsi:.2f} {'(Overbought)' if tech_data.rsi and tech_data.rsi > 70 else '(Oversold)' if tech_data.rsi and tech_data.rsi < 30 else '(Neutral)' if tech_data.rsi else 'N/A'}
- MACD Line: {tech_data.macd_line:.4f} | Signal: {tech_data.macd_signal:.4f} | Histogram: {tech_data.macd_histogram:.4f} {'(Bullish)' if tech_data.macd_line and tech_data.macd_signal and tech_data.macd_line > tech_data.macd_signal else '(Bearish)' if tech_data.macd_line and tech_data.macd_signal else 'N/A'}

MOVING AVERAGES:
- SMA 20: ${tech_data.sma_20:,.2f} {'(Above)' if tech_data.sma_20 and tech_data.current_price > tech_data.sma_20 else '(Below)' if tech_data.sma_20 else 'N/A'}
- SMA 50: ${tech_data.sma_50:,.2f} {'(Above)' if tech_data.sma_50 and tech_data.current_price > tech_data.sma_50 else '(Below)' if tech_data.sma_50 else 'N/A'}
- SMA 200: ${tech_data.sma_200:,.2f} {'(Above)' if tech_data.sma_200 and tech_data.current_price > tech_data.sma_200 else '(Below)' if tech_data.sma_200 else 'N/A'}
- EMA 20: ${tech_data.ema_20:,.2f} {'(Above)' if tech_data.ema_20 and tech_data.current_price > tech_data.ema_20 else '(Below)' if tech_data.ema_20 else 'N/A'}
- EMA 50: ${tech_data.ema_50:,.2f} {'(Above)' if tech_data.ema_50 and tech_data.current_price > tech_data.ema_50 else '(Below)' if tech_data.ema_50 else 'N/A'}

BOLLINGER BANDS:
- Upper: ${tech_data.bb_upper:,.2f} | Middle: ${tech_data.bb_middle:,.2f} | Lower: ${tech_data.bb_lower:,.2f}
- Position: {'Near Upper Band' if tech_data.bb_upper and tech_data.current_price > tech_data.bb_upper * 0.98 else 'Near Lower Band' if tech_data.bb_lower and tech_data.current_price < tech_data.bb_lower * 1.02 else 'Middle Range' if tech_data.bb_middle else 'N/A'}

ADX TREND ANALYSIS:
- ADX: {tech_data.adx:.2f} {'(Strong Trend)' if tech_data.adx and tech_data.adx > 25 else '(Weak Trend)' if tech_data.adx else 'N/A'}
- +DI: {tech_data.plus_di:.2f} | -DI: {tech_data.minus_di:.2f}
- Trend Direction: {'Bullish (+DI > -DI)' if tech_data.plus_di and tech_data.minus_di and tech_data.plus_di > tech_data.minus_di else 'Bearish (-DI > +DI)' if tech_data.plus_di and tech_data.minus_di else 'N/A'}

OSCILLATORS:
- Stochastic %K: {tech_data.stoch_k:.2f} | %D: {tech_data.stoch_d:.2f}
- Williams %R: {tech_data.williams_r:.2f} {'(Overbought)' if tech_data.williams_r and tech_data.williams_r > -20 else '(Oversold)' if tech_data.williams_r and tech_data.williams_r < -80 else '(Neutral)' if tech_data.williams_r else 'N/A'}
- CCI: {tech_data.cci:.2f} {'(Overbought)' if tech_data.cci and tech_data.cci > 100 else '(Oversold)' if tech_data.cci and tech_data.cci < -100 else '(Neutral)' if tech_data.cci else 'N/A'}

VOLUME INDICATORS:
- OBV: {tech_data.obv:,.0f} {'(Accumulation)' if tech_data.obv and tech_data.obv > 0 else '(Distribution)' if tech_data.obv and tech_data.obv < 0 else 'N/A' if tech_data.obv else 'N/A'}
- VWAP: ${tech_data.vwap:,.2f} {'(Above VWAP)' if tech_data.vwap and tech_data.current_price > tech_data.vwap else '(Below VWAP)' if tech_data.vwap else 'N/A'}

ICHIMOKU CLOUD:
- Tenkan-sen: ${tech_data.ichimoku_tenkan:,.2f} {'(Above)' if tech_data.ichimoku_tenkan and tech_data.current_price > tech_data.ichimoku_tenkan else '(Below)' if tech_data.ichimoku_tenkan else 'N/A'}
- Kijun-sen: ${tech_data.ichimoku_kijun:,.2f} {'(Above)' if tech_data.ichimoku_kijun and tech_data.current_price > tech_data.ichimoku_kijun else '(Below)' if tech_data.ichimoku_kijun else 'N/A'}
- Senkou Span A: {f"${tech_data.ichimoku_senkou_a:,.2f}" if tech_data.ichimoku_senkou_a is not None else "N/A"}
- Senkou Span B: {f"${tech_data.ichimoku_senkou_b:,.2f}" if tech_data.ichimoku_senkou_b is not None else "N/A"}

FIBONACCI LEVELS:
{chr(10).join([f"- {level}%: ${price:,.2f}" for level, price in tech_data.fibonacci_levels.items()]) if tech_data.fibonacci_levels else "N/A"}

SUPPORT LEVELS: {[f"${level:,.2f}" for level in tech_data.support_levels[:3]] if tech_data.support_levels else "N/A"}
RESISTANCE LEVELS: {[f"${level:,.2f}" for level in tech_data.resistance_levels[:3]] if tech_data.resistance_levels else "N/A"}

MARKET ANALYSIS:
- Trend Direction: {tech_data.trend_direction.upper() if tech_data.trend_direction else 'N/A'}
- Trend Strength: {tech_data.trend_strength.upper() if tech_data.trend_strength else 'N/A'}
- Market Phase: {tech_data.market_phase.upper() if tech_data.market_phase else 'N/A'}
        """
        
        return f"""
        {technical_info}
        
        You must provide a comprehensive technical analysis for {symbol.upper()} based on the REAL CALCULATED TECHNICAL DATA above in the EXACT JSON format below.
        
        REQUIRED JSON STRUCTURE:
        {{
          "title": "**COMPREHENSIVE TECHNICAL ANALYSIS: {symbol.upper()}**",
          "market_state": "Current market state based on ACTUAL price ${tech_data.current_price:,.2f} with {tech_data.price_change_24h:+.2f}% change. Market phase: {tech_data.market_phase.upper() if tech_data.market_phase else 'UNKNOWN'}",
          "trend_indicators": "ADX: {tech_data.adx:.2f} ({'STRONG' if tech_data.adx and tech_data.adx > 25 else 'WEAK'}) | +DI: {tech_data.plus_di:.2f} -DI: {tech_data.minus_di:.2f} | Ichimoku: {'BULLISH' if tech_data.ichimoku_tenkan and tech_data.ichimoku_kijun and tech_data.current_price > tech_data.ichimoku_tenkan else 'BEARISH'} | SMA20: ${tech_data.sma_20:,.2f} SMA50: ${tech_data.sma_50:,.2f} SMA200: ${tech_data.sma_200:,.2f} | MACD: {'BULLISH' if tech_data.macd_line and tech_data.macd_signal and tech_data.macd_line > tech_data.macd_signal else 'BEARISH'}",
          "oscillators": "RSI: {tech_data.rsi:.1f} ({'OVERBOUGHT' if tech_data.rsi and tech_data.rsi > 70 else 'OVERSOLD' if tech_data.rsi and tech_data.rsi < 30 else 'NEUTRAL'}) | Stochastic %K: {tech_data.stoch_k:.1f} %D: {tech_data.stoch_d:.1f} | Williams %R: {tech_data.williams_r:.1f} | CCI: {tech_data.cci:.1f}",
          "volume_indicators": "OBV: {tech_data.obv:,.0f} ({'ACCUMULATION' if tech_data.obv and tech_data.obv > 0 else 'DISTRIBUTION'}) | VWAP: ${tech_data.vwap:,.2f} ({'ABOVE' if tech_data.vwap and tech_data.current_price > tech_data.vwap else 'BELOW'}) | Volume: {tech_data.volume_24h:,.0f}",
          "fibonacci_levels": f"From High ${tech_data.high_24h:,.2f} to Low ${tech_data.low_24h:,.2f}: {fibonacci_text}",
          "elliott_wave": "Elliott Wave analysis based on {tech_data.trend_direction} trend at ${tech_data.current_price:,.2f}. Current wave assessment and projection targets based on price action pattern.",
          "smart_money_concepts": "Order Blocks analysis around ${tech_data.current_price:,.2f}. Fair Value Gaps identification. Liquidity pool analysis. Smart money positioning based on volume profile.",
          "trading_setup": f"Entry: Consider ${tech_data.current_price * 0.995:,.2f} (long) / ${tech_data.current_price * 1.005:,.2f} (short) | Stop Loss: {support_text} (long) | Take Profit: {resistance_text} (long)",
          "risk_assessment": f"Risk Level: {risk_level} | Volatility (ATR): {atr_text} | Trend Confidence: {tech_data.trend_strength.upper() if tech_data.trend_strength else 'UNKNOWN'}",
          "outlook": f"{trend_dir} bias with {trend_str} trend strength. Key levels: Support {support_level} | Resistance {resistance_level}"
        }}
        
        CRITICAL INSTRUCTIONS:
        - Use the REAL CALCULATED indicator values provided above - NO HALLUCINATION
        - All price levels and indicators are ACTUAL computed values from market data
        - Base trading signals on REAL RSI ({tech_data.rsi:.1f}), MACD ({tech_data.macd_line:.4f}), ADX ({tech_data.adx:.1f}) values
        - Reference ACTUAL support/resistance levels calculated from price action
        - Focus on {timeframe} timeframe with computed technical indicators
        - Return ONLY valid JSON, no other text
        {('- VERBOSE MODE: Fill ALL sections with detailed analysis. If data is missing, write "No data". Include all available indicators (RSI, MACD, ADX, Stoch, Williams %R, CCI, OBV, VWAP, ATR, SMAs/EMAs, Ichimoku, Fibonacci, Elliott Wave, Smart Money Concepts).' if verbose else '')}
        
        Symbol: {symbol.upper()}
        Real Current Price: ${tech_data.current_price:,.2f}
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