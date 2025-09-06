from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class Candle:
    t: int
    o: float
    h: float
    l: float
    c: float
    v: float


def _sma(arr: List[float], n: int) -> Optional[float]:
    if len(arr) < n:
        return None
    return sum(arr[-n:]) / n


def _ema(arr: List[float], n: int) -> Optional[float]:
    if len(arr) < n:
        return None
    k = 2 / (n + 1)
    ema = arr[-n]
    for x in arr[-n + 1 :]:
        ema = x * k + ema * (1 - k)
    return ema


def _rsi(closes: List[float], n: int = 14) -> Optional[float]:
    if len(closes) <= n:
        return None
    gains, losses = [], []
    for i in range(-n, -1):
        ch = closes[i + 1] - closes[i]
        gains.append(max(ch, 0.0))
        losses.append(abs(min(ch, 0.0)))
    avg_gain = sum(gains) / n
    avg_loss = sum(losses) / n
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _macd(closes: List[float]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    if len(closes) < 35:
        return (None, None, None)
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    if ema12 is None or ema26 is None:
        return (None, None, None)
    macd = ema12 - ema26
    # approximate signal from a short synthetic macd series
    macd_series: List[float] = []
    for i in range(len(closes) - 35, len(closes)):
        sub = closes[: i + 1]
        e12 = _ema(sub, 12)
        e26 = _ema(sub, 26)
        if e12 is not None and e26 is not None:
            macd_series.append(e12 - e26)
    signal = _ema(macd_series, 9) if len(macd_series) >= 9 else None
    hist = macd - signal if signal is not None else None
    return (macd, signal, hist)


def _typical_price(h: float, l: float, c: float) -> float:
    return (h + l + c) / 3.0


def _vwap(candles: List[Candle]) -> Optional[float]:
    if not candles:
        return None
    num = sum(_typical_price(x.h, x.l, x.c) * x.v for x in candles)
    den = sum(x.v for x in candles)
    return num / den if den else None


def _adx_dm(candles: List[Candle], n: int = 14) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    if len(candles) <= n:
        return (None, None, None)
    trs, dm_plus, dm_minus = [], [], []
    for i in range(1, len(candles)):
        h1, l1, c0 = candles[i].h, candles[i].l, candles[i - 1].c
        tr = max(h1 - l1, abs(h1 - c0), abs(l1 - c0))
        trs.append(tr)
        up_move = candles[i].h - candles[i - 1].h
        dn_move = candles[i - 1].l - candles[i].l
        dm_plus.append(up_move if (up_move > dn_move and up_move > 0) else 0.0)
        dm_minus.append(dn_move if (dn_move > up_move and dn_move > 0) else 0.0)
    if len(trs) < n:
        return (None, None, None)
    atr = sum(trs[-n:]) / n
    pdi = 100 * (sum(dm_plus[-n:]) / n) / atr if atr else 0.0
    mdi = 100 * (sum(dm_minus[-n:]) / n) / atr if atr else 0.0
    # crude ADX using last window
    dx = 100 * abs(pdi - mdi) / (pdi + mdi) if (pdi + mdi) else 0.0
    return (dx, pdi, mdi)


def _stoch(candles: List[Candle], n: int = 14, d: int = 3) -> Tuple[Optional[float], Optional[float]]:
    if len(candles) < n + d:
        return (None, None)
    k_vals: List[float] = []
    for i in range(len(candles) - n, len(candles)):
        window = candles[i - n + 1 : i + 1]
        hh = max(x.h for x in window)
        ll = min(x.l for x in window)
        k = 100 * (candles[i].c - ll) / (hh - ll) if hh > ll else 50.0
        k_vals.append(k)
    k = k_vals[-1]
    dval = sum(k_vals[-d:]) / d
    return (k, dval)


def _williams_r(candles: List[Candle], n: int = 14) -> Optional[float]:
    if len(candles) < n:
        return None
    window = candles[-n:]
    hh = max(x.h for x in window)
    ll = min(x.l for x in window)
    return -100 * (window[-1].c - hh) / (hh - ll) if hh > ll else -50.0


def _cci(candles: List[Candle], n: int = 20) -> Optional[float]:
    if len(candles) < n:
        return None
    tps = [_typical_price(x.h, x.l, x.c) for x in candles[-n:]]
    sma = sum(tps) / n
    md = sum(abs(tp - sma) for tp in tps) / n
    return (tps[-1] - sma) / (0.015 * md) if md else 0.0


def _obv(candles: List[Candle]) -> Optional[float]:
    if len(candles) < 2:
        return None
    obv = 0.0
    for i in range(1, len(candles)):
        if candles[i].c > candles[i - 1].c:
            obv += candles[i].v
        elif candles[i].c < candles[i - 1].c:
            obv -= candles[i].v
    return obv


def _cmf(candles: List[Candle], n: int = 20) -> Optional[float]:
    if len(candles) < n:
        return None
    win = candles[-n:]
    mfv = 0.0
    vol = 0.0
    for x in win:
        tp = _typical_price(x.h, x.l, x.c)
        mfm = ((tp - x.l) - (x.h - tp)) / (x.h - x.l) if (x.h > x.l) else 0.0
        mfv += mfm * x.v
        vol += x.v
    return mfv / vol if vol else 0.0


def _ichimoku(candles: List[Candle]) -> Dict[str, float]:
    if len(candles) < 26:
        return {}
    highs = [c.h for c in candles]
    lows = [c.l for c in candles]
    def _highest(arr: List[float], n: int) -> float:
        return max(arr[-n:])
    def _lowest(arr: List[float], n: int) -> float:
        return min(arr[-n:])
    tenkan = (_highest(highs, 9) + _lowest(lows, 9)) / 2
    kijun = (_highest(highs, 26) + _lowest(lows, 26)) / 2
    span_a = (tenkan + kijun) / 2
    if len(candles) >= 52:
        span_b = (_highest(highs, 52) + _lowest(lows, 52)) / 2
    else:
        span_b = None
    cloud_top = max(span_a, span_b) if (span_b is not None) else span_a
    cloud_bottom = min(span_a, span_b) if (span_b is not None) else span_a
    thickness = abs((cloud_top or 0) - (cloud_bottom or 0))
    return {
        "tenkan": tenkan,
        "kijun": kijun,
        "kumo_top": cloud_top,
        "kumo_bottom": cloud_bottom,
        "kumo_thickness": thickness,
    }


def _volume_profile(candles: List[Candle], bins: int = 12) -> Dict[str, float]:
    if not candles:
        return {}
    lo = min(c.l for c in candles)
    hi = max(c.h for c in candles)
    if hi <= lo:
        return {}
    step = (hi - lo) / bins
    buckets = [0.0] * (bins)
    for c in candles:
        tp = _typical_price(c.h, c.l, c.c)
        idx = min(int((tp - lo) / step), bins - 1)
        buckets[idx] += c.v
    max_i = max(range(bins), key=lambda i: buckets[i])
    poc = lo + (max_i + 0.5) * step
    mean = sum((lo + (i + 0.5) * step) * buckets[i] for i in range(bins)) / sum(buckets) if sum(buckets) > 0 else poc
    vah = mean + step * 2
    val = mean - step * 2
    return {"poc": poc, "value_area_low": val, "value_area_high": vah}


def build_structured_from_candles(symbol: str, candles: List[Candle], timeframe_label: str = "4h") -> Dict[str, Any]:
    if not candles:
        return {
            "title": f"COMPREHENSIVE TECHNICAL ANALYSIS: {symbol}",
            "sections": {"outlook": {"content": {"bias": "NEUTRAL", "summary": "No data"}}},
        }

    closes = [c.c for c in candles]
    price = closes[-1]
    change = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) > 1 else 0.0
    vol24 = sum(c.v for c in candles[-min(len(candles), 42) :])

    rsi = _rsi(closes)
    macd, macd_signal, macd_hist = _macd(closes)
    adx, di_plus, di_minus = _adx_dm(candles)
    k, d = _stoch(candles)
    wr = _williams_r(candles)
    cci = _cci(candles)
    vwap = _vwap(candles)
    obv = _obv(candles)
    cmf = _cmf(candles)
    ich = _ichimoku(candles)
    vp = _volume_profile(candles)

    phase = (
        "BULLISH"
        if (macd_hist or 0) > 0 and (rsi or 50) >= 50
        else "BEARISH" if (macd_hist or 0) < 0 and (rsi or 50) < 50
        else "NEUTRAL"
    )

    indicators = {
        "rsi": rsi,
        "macd": macd,
        "macd_signal": macd_signal,
        "macd_histogram": macd_hist,
        "adx": adx,
        "di_plus": di_plus,
        "di_minus": di_minus,
        "stochastic_k": k,
        "stochastic_d": d,
        "williams_r": wr,
        "cci": cci,
        "obv": obv,
        "cmf": cmf,
        "vwap": vwap,
        **ich,
        **vp,
        "volume_delta": (candles[-1].v - candles[-2].v) if len(candles) > 1 else 0.0,
        "force_index": (closes[-1] - closes[-2]) * (candles[-1].v) if len(candles) > 1 else 0.0,
    }

    structured = {
        "title": f"COMPREHENSIVE TECHNICAL ANALYSIS: {symbol}",
        "sections": {
            "market_state": {
                "content": {
                    "price": price,
                    "change_24h": change,
                    "volume_24h": vol24,
                    "phase": phase,
                    "description": f"Current price ${price:,.2f}, {change:+.2f}% 24h; phase {phase}",
                }
            },
            "trading_levels": {
                "content": {
                    "support": sorted([vp.get("value_area_low", price * 0.98)]) if vp else [],
                    "resistance": sorted([ich.get("kijun", price * 1.01), ich.get("kumo_top", price * 1.02)]) if ich else [],
                    "trading_range": {
                        "low": min(c.l for c in candles[-min(len(candles), 60) :]),
                        "high": max(c.h for c in candles[-min(len(candles), 60) :]),
                    },
                }
            },
            "indicator_analysis": {
                "content": {
                    "indicators": indicators,
                    "description": "Local technical snapshot (RSI/MACD/ADX/Stoch/W%R/CCI/OBV/CMF/VWAP/Ichimoku/Volume Profile).",
                }
            },
            "timeframe_analysis": {
                "content": {
                    "1h": {"trend": "NEUTRAL", "strength": "MODERATE"},
                    "4h": {"trend": phase, "strength": "STRONG" if (adx or 0) >= 25 else "MODERATE"},
                    "1d": {"trend": phase, "strength": "MODERATE"},
                }
            },
            "risk_assessment": {
                "content": {"risk_level": "LOW" if (adx or 0) < 20 else "MODERATE", "position_size": "10%", "risk_reward": "1:2"}
            },
            "outlook": {
                "content": {
                    "bias": "BULLISH" if phase == "BULLISH" else "BEARISH" if phase == "BEARISH" else "NEUTRAL",
                    "summary": "Structured, indicator-complete view.",
                }
            },
            "volume_analysis": {
                "content": {
                    "description": f"POC ${vp.get('poc', 0):.2f} | VAL ${vp.get('value_area_low', 0):.2f} | VAH ${vp.get('value_area_high', 0):.2f} | ΔVol {indicators['volume_delta']:.0f}"
                }
            },
            "trend_indicators": {"content": {"description": f"Ichimoku {'bearish' if price < (ich.get('kumo_top') or 0) else 'bullish'}; ADX {(adx or 0):.2f}"}},
            "oscillators": {"content": {"description": f"RSI {(rsi or 0):.1f}; StochK {(k or 0):.1f} StochD {(d or 0):.1f}; W%R {(wr or 0):.1f}; CCI {(cci or 0):.1f}"}},
            "trading_setup": {"content": {"description": "Breakout above kijun/VAH or breakdown below VAL/kumo bottom with tight stops."}},
        },
    }
    return structured

