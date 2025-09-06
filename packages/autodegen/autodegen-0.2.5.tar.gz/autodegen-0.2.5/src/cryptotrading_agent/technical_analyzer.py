"""
Real Technical Analysis Engine - Same quality as backend crew system.
"""

from __future__ import annotations

import asyncio
import logging
import numpy as np
import pandas as pd
import aiohttp
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    logging.warning("TA-Lib not available. Install with: pip install TA-Lib")

logger = logging.getLogger(__name__)


@dataclass
class TechnicalData:
    """Technical analysis results structure"""
    symbol: str
    timeframe: str
    timestamp: datetime
    
    # Price data
    current_price: float
    price_change_24h: float
    volume_24h: float
    high_24h: float  
    low_24h: float
    
    # Technical indicators
    rsi: Optional[float] = None
    macd_line: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    
    # Trend indicators
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    
    # Bollinger Bands
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    
    # Volume indicators
    obv: Optional[float] = None
    vwap: Optional[float] = None
    
    # Momentum indicators
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None
    williams_r: Optional[float] = None
    cci: Optional[float] = None
    
    # Volatility
    atr: Optional[float] = None
    
    # ADX trend strength
    adx: Optional[float] = None
    plus_di: Optional[float] = None
    minus_di: Optional[float] = None
    
    # Ichimoku
    ichimoku_tenkan: Optional[float] = None
    ichimoku_kijun: Optional[float] = None
    ichimoku_senkou_a: Optional[float] = None
    ichimoku_senkou_b: Optional[float] = None
    
    # Fibonacci levels
    fibonacci_levels: Optional[Dict[str, float]] = field(default_factory=dict)
    
    # Support/Resistance
    support_levels: List[float] = field(default_factory=list)
    resistance_levels: List[float] = field(default_factory=list)
    
    # Additional analysis
    trend_direction: Optional[str] = None
    trend_strength: Optional[str] = None
    market_phase: Optional[str] = None
    
    
class TechnicalAnalyzer:
    """Real technical analysis engine with full indicator calculations."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def fetch_ohlcv_data(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 500
    ) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data from Binance API."""
        try:
            # Ensure we have a session
            if not self.session or self.session.closed:
                if self.session and not self.session.closed:
                    await self.session.close()
                self.session = aiohttp.ClientSession()
                
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                "symbol": f"{symbol}USDT",
                "interval": interval,
                "limit": limit
            }
            
            logger.info(f"Fetching OHLCV data for {symbol} from {url}")
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Convert to pandas DataFrame
                    df = pd.DataFrame(data, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_asset_volume', 'number_of_trades',
                        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                    ])
                    
                    # Convert data types
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Set timestamp as index
                    df.set_index('timestamp', inplace=True)
                    
                    logger.info(f"Fetched {len(df)} candles for {symbol}")
                    return df
                else:
                    logger.error(f"Failed to fetch data: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching OHLCV data for {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate RSI using TA-Lib or manual calculation."""
        try:
            if TALIB_AVAILABLE:
                rsi_values = talib.RSI(prices.values, timeperiod=period)
                return float(rsi_values[-1]) if not np.isnan(rsi_values[-1]) else None
            else:
                # Manual RSI calculation
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None
    
    def calculate_macd(
        self, 
        prices: pd.Series, 
        fast_period: int = 12, 
        slow_period: int = 26, 
        signal_period: int = 9
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate MACD line, signal line, and histogram."""
        try:
            if TALIB_AVAILABLE:
                macd_line, macd_signal, macd_hist = talib.MACD(
                    prices.values,
                    fastperiod=fast_period,
                    slowperiod=slow_period,
                    signalperiod=signal_period
                )
                return (
                    float(macd_line[-1]) if not np.isnan(macd_line[-1]) else None,
                    float(macd_signal[-1]) if not np.isnan(macd_signal[-1]) else None,
                    float(macd_hist[-1]) if not np.isnan(macd_hist[-1]) else None
                )
            else:
                # Manual MACD calculation
                ema_fast = prices.ewm(span=fast_period).mean()
                ema_slow = prices.ewm(span=slow_period).mean()
                macd_line = ema_fast - ema_slow
                macd_signal = macd_line.ewm(span=signal_period).mean()
                macd_hist = macd_line - macd_signal
                
                return (
                    float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None,
                    float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else None,
                    float(macd_hist.iloc[-1]) if not pd.isna(macd_hist.iloc[-1]) else None
                )
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return None, None, None
    
    def calculate_bollinger_bands(
        self, 
        prices: pd.Series, 
        period: int = 20, 
        std_dev: float = 2.0
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate Bollinger Bands."""
        try:
            if TALIB_AVAILABLE:
                upper, middle, lower = talib.BBANDS(
                    prices.values,
                    timeperiod=period,
                    nbdevup=std_dev,
                    nbdevdn=std_dev,
                    matype=0
                )
                return (
                    float(upper[-1]) if not np.isnan(upper[-1]) else None,
                    float(middle[-1]) if not np.isnan(middle[-1]) else None,
                    float(lower[-1]) if not np.isnan(lower[-1]) else None
                )
            else:
                # Manual BB calculation
                sma = prices.rolling(window=period).mean()
                std = prices.rolling(window=period).std()
                upper = sma + (std_dev * std)
                lower = sma - (std_dev * std)
                
                return (
                    float(upper.iloc[-1]) if not pd.isna(upper.iloc[-1]) else None,
                    float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else None,
                    float(lower.iloc[-1]) if not pd.isna(lower.iloc[-1]) else None
                )
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return None, None, None
    
    def calculate_adx(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate ADX, +DI, -DI."""
        try:
            if TALIB_AVAILABLE:
                adx_values = talib.ADX(high.values, low.values, close.values, timeperiod=period)
                plus_di = talib.PLUS_DI(high.values, low.values, close.values, timeperiod=period)
                minus_di = talib.MINUS_DI(high.values, low.values, close.values, timeperiod=period)
                
                return (
                    float(adx_values[-1]) if not np.isnan(adx_values[-1]) else None,
                    float(plus_di[-1]) if not np.isnan(plus_di[-1]) else None,
                    float(minus_di[-1]) if not np.isnan(minus_di[-1]) else None
                )
            else:
                # Manual ADX calculation (simplified)
                tr1 = high - low
                tr2 = (high - close.shift()).abs()
                tr3 = (low - close.shift()).abs()
                tr = pd.DataFrame([tr1, tr2, tr3]).max()
                
                plus_dm = (high - high.shift()).where((high - high.shift()) > (low.shift() - low), 0)
                minus_dm = (low.shift() - low).where((low.shift() - low) > (high - high.shift()), 0)
                
                tr_smooth = tr.ewm(span=period).mean()
                plus_dm_smooth = plus_dm.ewm(span=period).mean()
                minus_dm_smooth = minus_dm.ewm(span=period).mean()
                
                plus_di = 100 * (plus_dm_smooth / tr_smooth)
                minus_di = 100 * (minus_dm_smooth / tr_smooth)
                
                dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di))
                adx = dx.ewm(span=period).mean()
                
                return (
                    float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else None,
                    float(plus_di.iloc[-1]) if not pd.isna(plus_di.iloc[-1]) else None,
                    float(minus_di.iloc[-1]) if not pd.isna(minus_di.iloc[-1]) else None
                )
        except Exception as e:
            logger.error(f"Error calculating ADX: {e}")
            return None, None, None
    
    def calculate_stochastic(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[Optional[float], Optional[float]]:
        """Calculate Stochastic Oscillator %K and %D."""
        try:
            if TALIB_AVAILABLE:
                stoch_k, stoch_d = talib.STOCH(
                    high.values, low.values, close.values,
                    fastk_period=k_period,
                    slowk_period=d_period,
                    slowd_period=d_period
                )
                return (
                    float(stoch_k[-1]) if not np.isnan(stoch_k[-1]) else None,
                    float(stoch_d[-1]) if not np.isnan(stoch_d[-1]) else None
                )
            else:
                # Manual stochastic calculation
                lowest_low = low.rolling(window=k_period).min()
                highest_high = high.rolling(window=k_period).max()
                k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
                d_percent = k_percent.rolling(window=d_period).mean()
                
                return (
                    float(k_percent.iloc[-1]) if not pd.isna(k_percent.iloc[-1]) else None,
                    float(d_percent.iloc[-1]) if not pd.isna(d_percent.iloc[-1]) else None
                )
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return None, None
    
    def calculate_fibonacci_levels(
        self,
        high_price: float,
        low_price: float
    ) -> Dict[str, float]:
        """Calculate Fibonacci retracement levels."""
        try:
            price_range = high_price - low_price
            
            levels = {
                "0.0": high_price,
                "23.6": high_price - (price_range * 0.236),
                "38.2": high_price - (price_range * 0.382),
                "50.0": high_price - (price_range * 0.5),
                "61.8": high_price - (price_range * 0.618),
                "78.6": high_price - (price_range * 0.786),
                "100.0": low_price
            }
            
            return levels
            
        except Exception as e:
            logger.error(f"Error calculating Fibonacci levels: {e}")
            return {}
    
    def calculate_ichimoku(
        self,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series
    ) -> Dict[str, Optional[float]]:
        """Calculate Ichimoku Cloud components."""
        try:
            # Tenkan-sen (9-period high-low average)
            tenkan_high = high.rolling(window=9).max()
            tenkan_low = low.rolling(window=9).min()
            tenkan_sen = (tenkan_high + tenkan_low) / 2
            
            # Kijun-sen (26-period high-low average)
            kijun_high = high.rolling(window=26).max()
            kijun_low = low.rolling(window=26).min()
            kijun_sen = (kijun_high + kijun_low) / 2
            
            # Senkou Span A (Leading Span A)
            senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
            
            # Senkou Span B (Leading Span B)
            senkou_high = high.rolling(window=52).max()
            senkou_low = low.rolling(window=52).min()
            senkou_span_b = ((senkou_high + senkou_low) / 2).shift(26)
            
            return {
                "tenkan_sen": float(tenkan_sen.iloc[-1]) if not pd.isna(tenkan_sen.iloc[-1]) else None,
                "kijun_sen": float(kijun_sen.iloc[-1]) if not pd.isna(kijun_sen.iloc[-1]) else None,
                "senkou_span_a": float(senkou_span_a.iloc[-1]) if not pd.isna(senkou_span_a.iloc[-1]) else None,
                "senkou_span_b": float(senkou_span_b.iloc[-1]) if not pd.isna(senkou_span_b.iloc[-1]) else None
            }
            
        except Exception as e:
            logger.error(f"Error calculating Ichimoku: {e}")
            return {"tenkan_sen": None, "kijun_sen": None, "senkou_span_a": None, "senkou_span_b": None}
    
    async def analyze_symbol(self, symbol: str, timeframe: str = "1h") -> Optional[TechnicalData]:
        """Perform comprehensive technical analysis on a symbol."""
        try:
            logger.info(f"Starting comprehensive technical analysis for {symbol} ({timeframe})")
            
            # Fetch OHLCV data
            df = await self.fetch_ohlcv_data(symbol, timeframe, limit=500)
            if df is None or df.empty:
                logger.error(f"No data available for {symbol}")
                return None
            
            # Get current market data
            current_data = await self._fetch_current_market_data(symbol)
            if not current_data:
                logger.error(f"Failed to fetch current market data for {symbol}")
                return None
            
            # Extract price series
            close_prices = df['close']
            high_prices = df['high'] 
            low_prices = df['low']
            volume = df['volume']
            
            # Initialize technical data structure
            tech_data = TechnicalData(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.now(timezone.utc),
                current_price=current_data['price'],
                price_change_24h=current_data['change_24h'],
                volume_24h=current_data['volume_24h'],
                high_24h=current_data['high_24h'],
                low_24h=current_data['low_24h']
            )
            
            # Calculate all technical indicators
            logger.info("Calculating technical indicators...")
            
            # RSI
            tech_data.rsi = self.calculate_rsi(close_prices)
            
            # MACD
            tech_data.macd_line, tech_data.macd_signal, tech_data.macd_histogram = self.calculate_macd(close_prices)
            
            # Moving Averages
            tech_data.sma_20 = float(close_prices.rolling(window=20).mean().iloc[-1]) if not pd.isna(close_prices.rolling(window=20).mean().iloc[-1]) else None
            tech_data.sma_50 = float(close_prices.rolling(window=50).mean().iloc[-1]) if not pd.isna(close_prices.rolling(window=50).mean().iloc[-1]) else None
            tech_data.sma_200 = float(close_prices.rolling(window=200).mean().iloc[-1]) if not pd.isna(close_prices.rolling(window=200).mean().iloc[-1]) else None
            tech_data.ema_20 = float(close_prices.ewm(span=20).mean().iloc[-1]) if not pd.isna(close_prices.ewm(span=20).mean().iloc[-1]) else None
            tech_data.ema_50 = float(close_prices.ewm(span=50).mean().iloc[-1]) if not pd.isna(close_prices.ewm(span=50).mean().iloc[-1]) else None
            
            # Bollinger Bands
            tech_data.bb_upper, tech_data.bb_middle, tech_data.bb_lower = self.calculate_bollinger_bands(close_prices)
            
            # ADX
            tech_data.adx, tech_data.plus_di, tech_data.minus_di = self.calculate_adx(high_prices, low_prices, close_prices)
            
            # Stochastic
            tech_data.stoch_k, tech_data.stoch_d = self.calculate_stochastic(high_prices, low_prices, close_prices)
            
            # Williams %R
            if TALIB_AVAILABLE:
                willr = talib.WILLR(high_prices.values, low_prices.values, close_prices.values, timeperiod=14)
                tech_data.williams_r = float(willr[-1]) if not np.isnan(willr[-1]) else None
            
            # CCI
            if TALIB_AVAILABLE:
                cci = talib.CCI(high_prices.values, low_prices.values, close_prices.values, timeperiod=14)
                tech_data.cci = float(cci[-1]) if not np.isnan(cci[-1]) else None
            
            # ATR
            if TALIB_AVAILABLE:
                atr = talib.ATR(high_prices.values, low_prices.values, close_prices.values, timeperiod=14)
                tech_data.atr = float(atr[-1]) if not np.isnan(atr[-1]) else None
            
            # OBV
            if TALIB_AVAILABLE:
                obv = talib.OBV(close_prices.values, volume.values)
                tech_data.obv = float(obv[-1]) if not np.isnan(obv[-1]) else None
            
            # VWAP (simple approximation)
            typical_price = (high_prices + low_prices + close_prices) / 3
            tech_data.vwap = float((typical_price * volume).sum() / volume.sum()) if volume.sum() > 0 else None
            
            # Ichimoku
            ichimoku_data = self.calculate_ichimoku(high_prices, low_prices, close_prices)
            tech_data.ichimoku_tenkan = ichimoku_data['tenkan_sen']
            tech_data.ichimoku_kijun = ichimoku_data['kijun_sen'] 
            tech_data.ichimoku_senkou_a = ichimoku_data['senkou_span_a']
            tech_data.ichimoku_senkou_b = ichimoku_data['senkou_span_b']
            
            # Fibonacci levels
            tech_data.fibonacci_levels = self.calculate_fibonacci_levels(
                current_data['high_24h'],
                current_data['low_24h']
            )
            
            # Determine trend direction and strength
            tech_data.trend_direction = self._determine_trend_direction(tech_data)
            tech_data.trend_strength = self._determine_trend_strength(tech_data)
            tech_data.market_phase = self._determine_market_phase(tech_data)
            
            # Calculate support and resistance levels
            tech_data.support_levels = self._calculate_support_levels(tech_data, df)
            tech_data.resistance_levels = self._calculate_resistance_levels(tech_data, df)
            
            logger.info(f"Technical analysis completed for {symbol}")
            return tech_data
            
        except Exception as e:
            logger.error(f"Error in technical analysis for {symbol}: {e}")
            return None
    
    async def _fetch_current_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch current market data from Binance."""
        try:
            # Ensure we have a session
            if not self.session or self.session.closed:
                if self.session and not self.session.closed:
                    await self.session.close()
                self.session = aiohttp.ClientSession()
                
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {"symbol": f"{symbol}USDT"}
            
            logger.info(f"Fetching current market data for {symbol} from {url}")
            async with self.session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "price": float(data["lastPrice"]),
                        "change_24h": float(data["priceChangePercent"]),
                        "volume_24h": float(data["volume"]),
                        "high_24h": float(data["highPrice"]),
                        "low_24h": float(data["lowPrice"])
                    }
        except Exception as e:
            logger.error(f"Error fetching current market data: {e}")
            
        return None
    
    def _determine_trend_direction(self, data: TechnicalData) -> str:
        """Determine overall trend direction."""
        bullish_signals = 0
        bearish_signals = 0
        
        # SMA trend analysis
        if all([data.sma_20, data.sma_50, data.sma_200]):
            if data.current_price > data.sma_20 > data.sma_50 > data.sma_200:
                bullish_signals += 2
            elif data.current_price < data.sma_20 < data.sma_50 < data.sma_200:
                bearish_signals += 2
        
        # MACD signal
        if data.macd_line and data.macd_signal:
            if data.macd_line > data.macd_signal:
                bullish_signals += 1
            else:
                bearish_signals += 1
        
        # ADX directional movement
        if data.plus_di and data.minus_di:
            if data.plus_di > data.minus_di:
                bullish_signals += 1
            else:
                bearish_signals += 1
        
        if bullish_signals > bearish_signals:
            return "bullish"
        elif bearish_signals > bullish_signals:
            return "bearish"
        else:
            return "neutral"
    
    def _determine_trend_strength(self, data: TechnicalData) -> str:
        """Determine trend strength based on ADX."""
        if not data.adx:
            return "unknown"
        
        if data.adx > 50:
            return "very_strong"
        elif data.adx > 25:
            return "strong"
        elif data.adx > 20:
            return "moderate"
        else:
            return "weak"
    
    def _determine_market_phase(self, data: TechnicalData) -> str:
        """Determine current market phase."""
        if not data.rsi:
            return "unknown"
        
        if data.rsi > 70:
            return "overbought"
        elif data.rsi < 30:
            return "oversold"
        elif 45 <= data.rsi <= 55:
            return "neutral"
        elif data.rsi > 55:
            return "bullish"
        else:
            return "bearish"
    
    def _calculate_support_levels(self, data: TechnicalData, df: pd.DataFrame) -> List[float]:
        """Calculate dynamic support levels."""
        levels = []
        
        # Add Fibonacci support levels
        if data.fibonacci_levels:
            for level in ["78.6", "61.8", "50.0", "38.2"]:
                if level in data.fibonacci_levels:
                    levels.append(data.fibonacci_levels[level])
        
        # Add moving average support
        if data.sma_50 and data.current_price > data.sma_50:
            levels.append(data.sma_50)
        if data.sma_200 and data.current_price > data.sma_200:
            levels.append(data.sma_200)
        
        # Add Bollinger Band lower bound
        if data.bb_lower:
            levels.append(data.bb_lower)
        
        # Add Ichimoku support
        if data.ichimoku_kijun and data.current_price > data.ichimoku_kijun:
            levels.append(data.ichimoku_kijun)
        
        return sorted(list(set(levels)), reverse=True)
    
    def _calculate_resistance_levels(self, data: TechnicalData, df: pd.DataFrame) -> List[float]:
        """Calculate dynamic resistance levels."""
        levels = []
        
        # Add Fibonacci resistance levels
        if data.fibonacci_levels:
            for level in ["23.6", "38.2", "50.0", "61.8"]:
                if level in data.fibonacci_levels and data.fibonacci_levels[level] > data.current_price:
                    levels.append(data.fibonacci_levels[level])
        
        # Add moving average resistance
        if data.sma_50 and data.current_price < data.sma_50:
            levels.append(data.sma_50)
        if data.sma_200 and data.current_price < data.sma_200:
            levels.append(data.sma_200)
        
        # Add Bollinger Band upper bound
        if data.bb_upper:
            levels.append(data.bb_upper)
        
        # Add recent highs as resistance
        if not df.empty:
            recent_high = df['high'].tail(50).max()
            if recent_high > data.current_price:
                levels.append(float(recent_high))
        
        return sorted(list(set(levels)))


# Utility function for easy access
async def get_technical_analysis(symbol: str, timeframe: str = "1h") -> Optional[TechnicalData]:
    """Convenience function to get technical analysis for a symbol."""
    async with TechnicalAnalyzer() as analyzer:
        return await analyzer.analyze_symbol(symbol, timeframe)