from __future__ import annotations

from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def _format_price(x):
    if x is None:
        return "—"
    try:
        import math
        if isinstance(x, float) and math.isnan(x):
            return "—"
    except Exception:
        pass
    try:
        x = float(x)
        if x > 100:
            return f"${x:,.2f}"
        if x > 1:
            return f"${x:.4f}"
        return f"${x:.8f}"
    except Exception:
        return "—"


def _safe_num(x, money=False, precise=False, percent=False):
    if x is None:
        return "—"
    try:
        import math
        if isinstance(x, float) and math.isnan(x):
            return "—"
    except Exception:
        pass
    try:
        xf = float(x)
        if money:
            return _format_price(xf)
        if percent:
            return f"{xf:+.2f}%"
        if precise:
            return f"{xf:.4f}"
        return f"{xf:.2f}"
    except Exception:
        return "—"


def render_structured(structured: Dict[str, Any]) -> None:
    sections = (structured or {}).get("sections", {})

    # Title
    title = structured.get("title") or "COMPREHENSIVE TECHNICAL ANALYSIS"
    console.print(Panel.fit(title, border_style="bright_blue", box=box.DOUBLE))

    # Market State
    if "market_state" in sections:
        c = sections["market_state"].get("content", {})
        phase = (c.get("phase") or "NEUTRAL").upper()
        if phase not in ("BULLISH", "BEARISH", "NEUTRAL"):
            phase = "NEUTRAL"
        vol = c.get("volume_24h") or 0
        vol_s = f"${vol:,.0f}" if isinstance(vol, (int, float)) and vol > 0 else "—"
        panel = Panel(
            f"""[bold]Current Price:[/bold] {_safe_num(c.get('price'), money=True)}
[bold]24h Change:[/bold] [{'green' if (c.get('change_24h') or 0)>=0 else 'red'}]{_safe_num(c.get('change_24h'), percent=True)}[/]
[bold]24h Volume:[/bold] {vol_s}
[bold]Market Phase:[/bold] [{'green' if phase=='BULLISH' else 'red' if phase=='BEARISH' else 'yellow'}]{phase}[/]""",
            title="🏢 Market State",
            border_style="cyan",
        )
        console.print(panel)

    # Trading Levels
    if "trading_levels" in sections:
        c = sections["trading_levels"].get("content", {})
        table = Table(title="🧭 Trading Levels", box=box.ROUNDED)
        table.add_column("Support", style="red", justify="right")
        table.add_column("Current", style="cyan", justify="center")
        table.add_column("Resistance", style="green", justify="right")

        supports = c.get("support") or []
        resist = c.get("resistance") or []
        current = (sections.get("market_state", {}).get("content", {}) or {}).get("price", 0)
        rows = max(len(supports), len(resist), 1)
        tr = c.get("trading_range") or {}
        if tr and "low" in tr and "high" in tr:
            console.print(
                f"  [dim]Trading Range: {_safe_num(tr['low'], money=True)} - {_safe_num(tr['high'], money=True)}[/dim]"
            )

        for i in range(rows):
            s = _format_price(supports[i]) if i < len(supports) else ""
            r = _format_price(resist[i]) if i < len(resist) else ""
            cur = _format_price(current) if i == 0 else ""
            table.add_row(s, cur, r)
        console.print(table)

    # Indicators table
    ind = {}
    if "indicator_analysis" in sections:
        content = sections["indicator_analysis"].get("content", {})
        ind = content.get("indicators") or {}

    if "timeframe_analysis" in sections:
        tfc = sections["timeframe_analysis"].get("content", {})
        for tf in ("1h", "4h", "1d"):
            blob = (tfc.get(tf) or {}).get("indicators") or {}
            for k, v in blob.items():
                ind.setdefault(k, v)

    if ind:
        t = Table(title="🔬 Technical Indicators", box=box.SIMPLE_HEAD)
        t.add_column("Indicator", style="cyan", width=18)
        t.add_column("Value", style="bold", justify="right")
        t.add_column("Status / Detail", style="yellow")

        # RSI
        rsi = ind.get("rsi")
        if rsi is not None:
            status = "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
            color = "red" if rsi < 30 else "green" if rsi > 70 else "yellow"
            t.add_row("RSI (14)", _safe_num(rsi), f"[{color}]{status}[/]")
        else:
            t.add_row("RSI (14)", "—", "—")

        # MACD
        macd = ind.get("macd")
        sig = ind.get("macd_signal")
        hist = ind.get("macd_histogram")
        if macd is not None or sig is not None or hist is not None:
            hstat = "Bullish" if (hist or 0) > 0 else "Bearish"
            hcol = "green" if (hist or 0) > 0 else "red"
            t.add_row("MACD", _safe_num(macd, precise=True), f"[{hcol}]{hstat}[/]")
            if sig is not None:
                t.add_row("  Signal", _safe_num(sig, precise=True), "")
            if hist is not None:
                t.add_row("  Histogram", _safe_num(hist, precise=True), "")
        else:
            t.add_row("MACD", "—", "—")

        # ADX (+DI/-DI)
        adx = ind.get("adx")
        if adx is not None:
            strength = "Strong Trend" if adx > 25 else "Weak Trend"
            scolor = "green" if adx > 25 else "yellow"
            t.add_row("ADX", _safe_num(adx), f"[{scolor}]{strength}[/]")
            dip = ind.get("di_plus")
            dim = ind.get("di_minus")
            if dip is not None or dim is not None:
                bias = ""
                if isinstance(dip, (int, float)) and isinstance(dim, (int, float)):
                    bias = (
                        "Bullish DI Bias" if dip > dim else "Bearish DI Bias" if dim > dip else "Balanced"
                    )
                t.add_row("  +DI / -DI", f"{_safe_num(dip)} / {_safe_num(dim)}", bias)
        else:
            t.add_row("ADX", "—", "—")

        # Stochastic
        k = ind.get("stochastic_k")
        d = ind.get("stochastic_d")
        if k is not None:
            s = "Oversold" if k < 20 else "Overbought" if k > 80 else "Neutral"
            col = "red" if k < 20 else "green" if k > 80 else "yellow"
            t.add_row("Stochastic", f"K={_safe_num(k)} D={_safe_num(d)}", f"[{col}]{s}[/]")
        else:
            t.add_row("Stochastic", "—", "—")

        # Williams %R
        wr = ind.get("williams_r")
        if wr is not None:
            s = "Oversold" if wr < -80 else "Overbought" if wr > -20 else "Neutral"
            col = "red" if wr < -80 else "green" if wr > -20 else "yellow"
            t.add_row("Williams %R", _safe_num(wr), f"[{col}]{s}[/]")
        else:
            t.add_row("Williams %R", "—", "—")

        # CCI
        cci = ind.get("cci")
        if cci is not None:
            s = "Oversold" if cci < -100 else "Overbought" if cci > 100 else "Neutral"
            col = "red" if cci < -100 else "green" if cci > 100 else "yellow"
            t.add_row("CCI", _safe_num(cci), f"[{col}]{s}[/]")
        else:
            t.add_row("CCI", "—", "—")

        # OBV + CMF
        obv = ind.get("obv")
        if obv is not None:
            t.add_row("OBV", _safe_num(obv), "Volume Trend")
        cmf = ind.get("cmf")
        if cmf is not None:
            s = "Accumulation" if cmf > 0 else "Distribution"
            col = "green" if cmf > 0 else "red"
            t.add_row("CMF", _safe_num(cmf, precise=True), f"[{col}]{s}[/]")

        # VWAP
        vwap = ind.get("vwap")
        cur = (sections.get("market_state", {}).get("content", {}) or {}).get("price", 0)
        if vwap is not None:
            s = "Above VWAP" if (cur or 0) > vwap else "Below VWAP"
            col = "green" if (cur or 0) > vwap else "red"
            t.add_row("VWAP", _safe_num(vwap, money=True), f"[{col}]{s}[/]")

        # Ichimoku (T/K + Cloud)
        ten = ind.get("tenkan")
        kij = ind.get("kijun")
        if ten is not None or kij is not None:
            t.add_row("Ichimoku", f"T={_safe_num(ten, money=True)} K={_safe_num(kij, money=True)}", "Conversion/Base")
        ct = ind.get("kumo_top")
        cb = ind.get("kumo_bottom")
        if ct is not None or cb is not None:
            t.add_row("  Cloud", f"{_safe_num(cb, money=True)} - {_safe_num(ct, money=True)}", "Kumo Range")
        th = ind.get("kumo_thickness")
        if th is not None:
            t.add_row("  Thickness", _safe_num(th), "Cloud Density")

        # Volume Profile + Delta + Force Index
        poc = ind.get("poc")
        if poc is not None:
            t.add_row("POC", _safe_num(poc, money=True), "Volume Pivot")
        val = ind.get("value_area_low")
        vah = ind.get("value_area_high")
        if val is not None or vah is not None:
            t.add_row("Value Area", f"{_safe_num(val, money=True)} - {_safe_num(vah, money=True)}", "VAL - VAH")
        vdelta = ind.get("volume_delta")
        if isinstance(vdelta, (int, float)):
            vd_col = "green" if vdelta > 0 else "red" if vdelta < 0 else "yellow"
            vd_txt = "Bullish" if vdelta > 0 else "Bearish" if vdelta < 0 else "Neutral"
            t.add_row("Volume Delta", _safe_num(vdelta), f"[{vd_col}]{vd_txt}[/]")
        fi = ind.get("force_index")
        if isinstance(fi, (int, float)):
            fi_col = "green" if fi > 0 else "red"
            fi_txt = "Bullish" if fi > 0 else "Bearish"
            t.add_row("Force Index", _safe_num(fi), f"[{fi_col}]{fi_txt}[/]")

        console.print(t)

    # Timeframe Analysis
    if "timeframe_analysis" in sections:
        c = sections["timeframe_analysis"].get("content", {})
        tf = Table(title="🕒 Timeframe Analysis", box=box.SIMPLE_HEAD)
        tf.add_column("Timeframe", style="cyan")
        tf.add_column("Trend", style="bold")
        tf.add_column("Strength", style="yellow")
        for k in ("1h", "4h", "1d"):
            blob = c.get(k) or {}
            tr = (blob.get("trend") or "NEUTRAL").upper()
            st = (blob.get("strength") or "MODERATE").upper()
            trc = "green" if tr == "BULLISH" else "red" if tr == "BEARISH" else "yellow"
            stc = "green" if st == "STRONG" else "red" if st == "WEAK" else "yellow"
            tf.add_row(k.upper(), f"[{trc}]{tr}[/]", f"[{stc}]{st}[/]")
        console.print(tf)

    # Risk
    if "risk_assessment" in sections:
        c = sections["risk_assessment"].get("content", {})
        risk = (c.get("risk_level") or "MODERATE").upper()
        rcol = "red" if risk == "HIGH" else "yellow" if risk == "MODERATE" else "green"
        panel = Panel(
            f"""[bold]Risk Level:[/bold] [{rcol}]{risk}[/]
[bold]Suggested Position Size:[/bold] {c.get('position_size','10%')}
[bold]Risk/Reward Ratio:[/bold] {c.get('risk_reward','1:2')}""",
            title="⚠️ Risk Assessment",
            border_style="red",
        )
        console.print(panel)

    # Outlook
    if "outlook" in sections:
        c = sections["outlook"].get("content", {})
        bias = (c.get("bias") or "NEUTRAL").upper()
        bcol = "green" if bias == "BULLISH" else "red" if bias == "BEARISH" else "yellow"
        summary = c.get("summary") or "No summary available"
        panel = Panel(
            f"[bold]Overall Bias:[/bold] [{bcol}]{bias}[/]\n\n{summary}",
            title="🔮 Market Outlook",
            border_style="magenta",
        )
        console.print(panel)

