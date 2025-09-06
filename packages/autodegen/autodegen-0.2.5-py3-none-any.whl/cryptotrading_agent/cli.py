"""Command-line interface for CryptoTrading Agent."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Optional

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.rule import Rule
    from rich import print as rprint
except ImportError:
    typer = None
    Console = None
    Rule = None
    rprint = print

from .agent import TradingAgent
from .exceptions import TradingAgentError, ConfigurationError
from .structured_local import Candle, build_structured_from_candles
from .technical_analyzer import TechnicalAnalyzer
from .renderers.rich_structured import render_structured

app = typer.Typer(
    name="autodegen",
    help="Production-ready crypto trading analysis agent with LLM hardening",
    no_args_is_help=True
) if typer else None

console = Console() if Console else None


def handle_typer_import_error():
    """Handle missing typer dependency gracefully."""
    print("Error: CLI dependencies not installed.")
    print("Install with: pip install 'autodegen[cli]'")
    print("Or install typer and rich manually: pip install typer rich")
    sys.exit(1)


@app.command() if app else lambda: None
def analyze(
    symbol: str = typer.Argument(..., help="Cryptocurrency symbol to analyze (e.g., BTC, ETH)"),
    timeframe: str = typer.Option("1h", "--timeframe", "-t", help="Analysis timeframe (1h, 4h, 1d)"),
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, json, text"),
    structured: bool = typer.Option(True, "--structured/--unstructured", help="Use structured output schema"),
    engine: str = typer.Option("local", "--engine", help="analysis engine: local | llm"),
    timeout: float = typer.Option(30.0, "--timeout", help="Request timeout in seconds"),
    detail: bool = typer.Option(False, "--detail", help="Show detailed view (same as default)"),
    concise: bool = typer.Option(False, "--concise", help="Show concise view")
):
    """Analyze a cryptocurrency symbol and get trading insights."""
    if not typer:
        handle_typer_import_error()
    
    async def _analyze():
        try:
            verbose = (not concise)

            if engine.lower() == "local":
                # Use local structured engine: fetch OHLCV and compute indicators
                if console:
                    with console.status(f"[bold green]Analyzing {symbol.upper()} (local)..."):
                        async with TechnicalAnalyzer() as ta:
                            df = await ta.fetch_ohlcv_data(symbol.upper(), interval=timeframe, limit=200)
                else:
                    print(f"Analyzing {symbol.upper()} (local)...")
                    async with TechnicalAnalyzer() as ta:
                        df = await ta.fetch_ohlcv_data(symbol.upper(), interval=timeframe, limit=200)

                candles: list[Candle] = []
                if df is not None and len(df) > 0:
                    for ts, row in df.tail(200).iterrows():
                        try:
                            candles.append(
                                Candle(
                                    t=int(ts.timestamp()),
                                    o=float(row["open"]),
                                    h=float(row["high"]),
                                    l=float(row["low"]),
                                    c=float(row["close"]),
                                    v=float(row["volume"]),
                                )
                            )
                        except Exception:
                            continue

                structured_payload = build_structured_from_candles(symbol.upper(), candles, timeframe_label=timeframe)
                result = structured_payload
            else:
                # LLM engine path (requires FIREWORKS_API_KEY)
                agent = TradingAgent()
                if console:
                    with console.status(f"[bold green]Analyzing {symbol.upper()} (llm)..."):
                        result = await agent.analyze(
                            symbol=symbol.upper(),
                            timeframe=timeframe,
                            structured=structured,
                            timeout=timeout,
                            verbose=verbose,
                        )
                else:
                    print(f"Analyzing {symbol.upper()} (llm)...")
                    result = await agent.analyze(
                        symbol=symbol.upper(),
                        timeframe=timeframe,
                        structured=structured,
                        timeout=timeout,
                        verbose=verbose,
                    )
            
            # Output results
            if output_format == "json" and structured:
                print(json.dumps(result if isinstance(result, dict) else (result.dict() if hasattr(result, 'dict') else str(result)), indent=2))
            elif output_format == "rich" and console:
                if isinstance(result, dict) and "sections" in result:
                    render_structured(result)
                else:
                    _display_rich_analysis(result, symbol.upper(), concise=concise)
            else:
                print(json.dumps(result, indent=2) if isinstance(result, dict) else str(result))
                
        except ConfigurationError as e:
            error_msg = f"Configuration Error: {e.message}"
            if console:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            sys.exit(1)
        except TradingAgentError as e:
            error_msg = f"Analysis Error: {e.message}"
            if console:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            sys.exit(1)
        except Exception as e:
            error_msg = f"Unexpected Error: {e}"
            if console:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            sys.exit(1)
    
    # Run async function
    asyncio.run(_analyze())


@app.command() if app else lambda: None
def market():
    """Get cryptocurrency market overview."""
    if not typer:
        handle_typer_import_error()
    
    async def _market():
        try:
            agent = TradingAgent()
            
            if console:
                with console.status("[bold green]Getting market overview..."):
                    overview = await agent.get_market_overview()
            else:
                print("Getting market overview...")
                overview = await agent.get_market_overview()
            
            if console:
                console.print(Panel(Markdown(overview), title="Market Overview", border_style="blue"))
            else:
                print("\n=== Market Overview ===")
                print(overview)
                
        except Exception as e:
            error_msg = f"Market overview failed: {e}"
            if console:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            sys.exit(1)
    
    asyncio.run(_market())


@app.command() if app else lambda: None
def health():
    """Check agent health and component status."""
    if not typer:
        handle_typer_import_error()
    
    async def _health():
        try:
            agent = TradingAgent()
            health_status = await agent.health_check()
            
            if console:
                _display_rich_health(health_status)
            else:
                print(json.dumps(health_status, indent=2))
                
        except Exception as e:
            error_msg = f"Health check failed: {e}"
            if console:
                console.print(f"[red]{error_msg}[/red]")
            else:
                print(error_msg)
            sys.exit(1)
    
    asyncio.run(_health())


@app.command() if app else lambda: None
def symbols():
    """List supported cryptocurrency symbols."""
    if not typer:
        handle_typer_import_error()
    
    try:
        agent = TradingAgent()
        supported = agent.get_supported_symbols()
        
        if console:
            table = Table(title="Supported Cryptocurrency Symbols")
            table.add_column("Symbol", style="cyan", no_wrap=True)
            table.add_column("Name", style="white")
            
            # Simple symbol to name mapping
            names = {
                "BTC": "Bitcoin", "ETH": "Ethereum", "BNB": "BNB", "SOL": "Solana",
                "ADA": "Cardano", "XRP": "XRP", "DOT": "Polkadot", "AVAX": "Avalanche",
                "MATIC": "Polygon", "LINK": "Chainlink", "UNI": "Uniswap", "ATOM": "Cosmos"
            }
            
            for symbol in supported:
                table.add_row(symbol, names.get(symbol, "Unknown"))
            
            console.print(table)
        else:
            print("Supported symbols:")
            for symbol in supported:
                print(f"  {symbol}")
                
    except Exception as e:
        error_msg = f"Error listing symbols: {e}"
        if console:
            console.print(f"[red]{error_msg}[/red]")
        else:
            print(error_msg)


# Section order for comprehensive display
SECTION_ORDER = [
    ("title", "Title"),
    ("market_state", "🏢 Market State"),
    ("trend_indicators", "📈 Trend Indicators"),
    ("oscillators", "⚡ Oscillators"),
    ("volume_indicators", "📊 Volume Analysis"),
    ("fibonacci_levels", "🎯 Fibonacci Levels"),
    ("elliott_wave", "🌊 Elliott Wave"),
    ("smart_money_concepts", "💎 Smart Money Concepts"),
    ("trading_levels", "🧭 Trading Levels"),
    ("indicator_analysis", "🔬 Indicator Analysis"),
    ("timeframe_analysis", "🕒 Timeframe Analysis"),
    ("trading_setup", "🎯 Trading Setup"),
    ("risk_assessment", "⚠️ Risk Assessment"),
    ("outlook", "🔮 Outlook"),
]

def _val(x):
    """Return value or 'No data' if empty/None."""
    return (x or "").strip() or "No data"

def _display_rich_analysis(result, symbol: str, concise=False):
    """Display analysis results using rich formatting."""
    if not console:
        return
    
    try:
        if hasattr(result, 'dict'):
            data = result.dict()
            
            # FULL: comprehensive display with all sections (default behavior)
            if not concise:
                console.print(Rule(f"[bold]Analysis: {symbol}[/bold]"))
                
                blocks = []
                for key, label in SECTION_ORDER:
                    if key in data:
                        content = _val(data[key])
                        if key == "title":
                            # Title as header
                            console.print(Panel.fit(Markdown(f"**{content}**"), title=f"Analysis: {symbol}", border_style="green"))
                        else:
                            # All other sections as panels
                            blocks.append(Panel.fit(Markdown(f"**{label}**\n\n{content}"), border_style="blue"))
                
                for block in blocks:
                    console.print(block)
                    
            else:
                # STANDARD/CONCISE: original compact view
                console.print(Panel(data.get('title', 'Analysis'), title=f"Analysis: {symbol}", border_style="green"))
                
                compact_sections = [
                    ("market_state", "🏢 Market State"),
                    ("trend_indicators", "📈 Trend"),
                    ("oscillators", "⚡ Oscillators"),
                    ("volume_indicators", "📊 Volume"),
                    ("outlook", "🔮 Outlook")
                ]
                
                for key, label in compact_sections:
                    if key in data:
                        console.print(Panel.fit(Markdown(f"**{label}**\n\n{_val(data[key])}"), border_style="cyan"))
                        
        else:
            # Text result fallback
            console.print(Panel(Markdown(str(result)), title=f"Analysis: {symbol}", border_style="green"))
            
    except Exception as e:
        console.print(f"[yellow]Warning: Could not format output: {e}[/yellow]")
        console.print(str(result))


def _safe_num(x, money: bool = False, precise: bool = False, percent: bool = False) -> str:
    if x is None:
        return "—"
    try:
        xf = float(x)
        if money:
            if xf > 100:
                return f"${xf:,.2f}"
            elif xf > 1:
                return f"${xf:.4f}"
            else:
                return f"${xf:.8f}"
        if percent:
            return f"{xf:+.2f}%"
        if precise:
            return f"{xf:.4f}"
        return f"{xf:.2f}"
    except Exception:
        return str(x)


def _display_structured_rich(structured: dict):
    """Rich renderer for structured payload (demo-quality)."""
    if not console:
        print(json.dumps(structured, indent=2))
        return

    from rich import box
    title = structured.get("title", "Analysis")
    console.print(Panel.fit(title, border_style="bright_blue", title=""))

    sections = structured.get("sections", {})

    # Market State
    ms = sections.get("market_state", {}).get("content", {})
    if ms:
        phase = ms.get("phase", "NEUTRAL")
        vol = ms.get("volume_24h", 0) or 0
        vol_str = f"${vol:,.0f}" if vol > 0 else "—"
        phase_color = "green" if phase == "BULLISH" else "red" if phase == "BEARISH" else "yellow"
        console.print(
            Panel(
                f"""[bold]Current Price:[/bold] {_safe_num(ms.get('price'), money=True)}\n[bold]24h Change:[/bold] [{('green' if (ms.get('change_24h') or 0)>=0 else 'red')}] {_safe_num(ms.get('change_24h'), percent=True)}[/]\n[bold]24h Volume:[/bold] {vol_str}\n[bold]Market Phase:[/bold] [{phase_color}]{phase}[/]""",
                title="🏢 Market State",
                border_style="cyan",
            )
        )

    # Trading Levels
    tl = sections.get("trading_levels", {}).get("content", {})
    if tl:
        from rich.table import Table
        table = Table(title="🧭 Trading Levels", box=box.ROUNDED)
        table.add_column("Support", style="red", justify="right")
        table.add_column("Current", style="cyan", justify="center")
        table.add_column("Resistance", style="green", justify="right")
        supports = tl.get("support", []) or []
        resistances = tl.get("resistance", []) or []
        current = ms.get("price", 0)
        max_rows = max(len(supports), len(resistances)) if (supports or resistances) else 1
        tr = tl.get("trading_range")
        if isinstance(tr, dict) and "low" in tr and "high" in tr:
            console.print(
                f"  [dim]Trading Range: {_safe_num(tr['low'], money=True)} - {_safe_num(tr['high'], money=True)}[/dim]"
            )
        for i in range(max_rows):
            s = _safe_num(supports[i], money=True) if i < len(supports) else ""
            r = _safe_num(resistances[i], money=True) if i < len(resistances) else ""
            c = _safe_num(current, money=True) if i == 0 else ""
            table.add_row(s, c, r)
        console.print(table)

    # Indicators table
    ind = sections.get("indicator_analysis", {}).get("content", {}).get("indicators", {})
    if ind:
        from rich.table import Table
        t = Table(title="🔬 Technical Indicators", box=box.SIMPLE_HEAD)
        t.add_column("Indicator", style="cyan", width=18)
        t.add_column("Value", style="bold", justify="right")
        t.add_column("Status", style="yellow")

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
        macd_signal = ind.get("macd_signal")
        macd_hist = ind.get("macd_histogram")
        if macd is not None or macd_signal is not None or macd_hist is not None:
            hist_status = "Bullish" if (macd_hist or 0) > 0 else "Bearish"
            hist_color = "green" if (macd_hist or 0) > 0 else "red"
            t.add_row("MACD", _safe_num(macd, precise=True), f"[{hist_color}]{hist_status}[/]")
            if macd_signal is not None:
                t.add_row("  Signal", _safe_num(macd_signal, precise=True), "")
            if macd_hist is not None:
                t.add_row("  Histogram", _safe_num(macd_hist, precise=True), "")
        else:
            t.add_row("MACD", "—", "—")

        # ADX + DI
        adx = ind.get("adx")
        if adx is not None:
            ts = "Strong" if adx > 25 else "Weak"
            tc = "green" if adx > 25 else "yellow"
            t.add_row("ADX", _safe_num(adx), f"[{tc}]{ts} Trend[/]")
            dpi = ind.get("di_plus")
            dmi = ind.get("di_minus")
            if dpi is not None or dmi is not None:
                bias = None
                if isinstance(dpi, (int, float)) and isinstance(dmi, (int, float)):
                    bias = "Bullish DI Bias" if dpi > dmi else "Bearish DI Bias" if dmi > dpi else "Balanced"
                t.add_row("  +DI / -DI", f"{_safe_num(dpi)} / {_safe_num(dmi)}", bias or "")
        else:
            t.add_row("ADX", "—", "—")

        # Stochastic
        sk, sd = ind.get("stochastic_k"), ind.get("stochastic_d")
        if sk is not None:
            st = "Oversold" if sk < 20 else "Overbought" if sk > 80 else "Neutral"
            sc = "red" if sk < 20 else "green" if sk > 80 else "yellow"
            t.add_row("Stochastic", f"K={_safe_num(sk)} D={_safe_num(sd)}", f"[{sc}]{st}[/]")
        else:
            t.add_row("Stochastic", "—", "—")

        # Williams %R
        wr = ind.get("williams_r")
        if wr is not None:
            ws = "Oversold" if wr < -80 else "Overbought" if wr > -20 else "Neutral"
            wc = "red" if wr < -80 else "green" if wr > -20 else "yellow"
            t.add_row("Williams %R", _safe_num(wr), f"[{wc}]{ws}[/]")
        else:
            t.add_row("Williams %R", "—", "—")

        # CCI
        cci = ind.get("cci")
        if cci is not None:
            cs = "Oversold" if cci < -100 else "Overbought" if cci > 100 else "Neutral"
            cc = "red" if cci < -100 else "green" if cci > 100 else "yellow"
            t.add_row("CCI", _safe_num(cci), f"[{cc}]{cs}[/]")
        else:
            t.add_row("CCI", "—", "—")

        # OBV / CMF / VWAP
        obv = ind.get("obv")
        if obv is not None:
            t.add_row("OBV", _safe_num(obv), "Volume Trend")
        cmf = ind.get("cmf")
        if cmf is not None:
            cmfs = "Accumulation" if cmf > 0 else "Distribution"
            cmfc = "green" if cmf > 0 else "red"
            t.add_row("CMF", _safe_num(cmf, precise=True), f"[{cmfc}]{cmfs}[/]")
        vwap = ind.get("vwap")
        if vwap is not None:
            cp = ms.get("price", 0)
            vwaps = "Above VWAP" if (cp or 0) > vwap else "Below VWAP"
            vwapc = "green" if (cp or 0) > vwap else "red"
            t.add_row("VWAP", _safe_num(vwap, money=True), f"[{vwapc}]{vwaps}[/]")

        # Ichimoku
        tenkan = ind.get("tenkan")
        kijun = ind.get("kijun")
        if tenkan is not None or kijun is not None:
            t.add_row("Ichimoku", f"T={_safe_num(tenkan, money=True)} K={_safe_num(kijun, money=True)}", "Conversion/Base")
        ktop = ind.get("kumo_top")
        kbot = ind.get("kumo_bottom")
        if ktop is not None or kbot is not None:
            t.add_row("  Cloud", f"{_safe_num(kbot, money=True)} - {_safe_num(ktop, money=True)}", "Kumo Range")
        kth = ind.get("kumo_thickness")
        if kth is not None:
            t.add_row("  Thickness", _safe_num(kth), "Cloud Density")

        # Volume profile & force index
        poc = ind.get("poc")
        if poc is not None:
            t.add_row("POC", _safe_num(poc, money=True), "Volume Pivot")
        val = ind.get("value_area_low")
        vah = ind.get("value_area_high")
        if val is not None or vah is not None:
            t.add_row("Value Area", f"{_safe_num(val, money=True)} - {_safe_num(vah, money=True)}", "VAL - VAH")
        vdelta = ind.get("volume_delta")
        if vdelta is not None:
            vdc = "green" if vdelta > 0 else "red" if vdelta < 0 else "yellow"
            vds = "Bullish" if vdelta > 0 else "Bearish" if vdelta < 0 else "Neutral"
            t.add_row("Volume Delta", _safe_num(vdelta), f"[{vdc}]{vds}[/]")
        fi = ind.get("force_index")
        if fi is not None:
            fic = "green" if fi > 0 else "red"
            fis = "Bullish" if fi > 0 else "Bearish"
            t.add_row("Force Index", _safe_num(fi), f"[{fic}]{fis}[/]")

        console.print(t)

    # Timeframe analysis
    tf = sections.get("timeframe_analysis", {}).get("content", {})
    if tf:
        from rich.table import Table
        table = Table(title="🕒 Timeframe Analysis", box=box.SIMPLE_HEAD)
        table.add_column("Timeframe", style="cyan")
        table.add_column("Trend", style="bold")
        table.add_column("Strength", style="yellow")
        for key in ["1h", "4h", "1d"]:
            if key in tf and isinstance(tf[key], dict):
                trend = tf[key].get("trend", "NEUTRAL")
                strength = tf[key].get("strength", "MODERATE")
                tc = "green" if trend == "BULLISH" else "red" if trend == "BEARISH" else "yellow"
                sc = "green" if strength == "STRONG" else "red" if strength == "WEAK" else "yellow"
                table.add_row(key.upper(), f"[{tc}]{trend}[/]", f"[{sc}]{strength}[/]")
        console.print(table)

    # Risk Assessment
    ra = sections.get("risk_assessment", {}).get("content", {})
    if ra:
        rl = ra.get("risk_level", "MODERATE")
        rl_color = "red" if rl == "HIGH" else "yellow" if rl == "MODERATE" else "green"
        console.print(
            Panel(
                f"""[bold]Risk Level:[/bold] [{rl_color}]{rl}[/]\n[bold]Suggested Position Size:[/bold] {ra.get('position_size', '10%')}\n[bold]Risk/Reward Ratio:[/bold] {ra.get('risk_reward', '1:2')}""",
                title="⚠️ Risk Assessment",
                border_style="red",
            )
        )

    # Outlook
    out = sections.get("outlook", {}).get("content", {})
    if out:
        bias = out.get("bias", "NEUTRAL")
        bc = "green" if bias == "BULLISH" else "red" if bias == "BEARISH" else "yellow"
        console.print(
            Panel(
                f"""[bold]Overall Bias:[/bold] [{bc}]{bias}[/]\n\n{out.get('summary', '')}""",
                title="🔮 Market Outlook",
                border_style="magenta",
            )
        )


def _display_rich_health(health_status: dict):
    """Display health status using rich formatting."""
    if not console:
        return
    
    status_color = {
        "healthy": "green",
        "degraded": "yellow", 
        "unhealthy": "red"
    }.get(health_status["status"], "white")
    
    # Main status
    console.print(Panel(
        f"Status: [{status_color}]{health_status['status'].upper()}[/{status_color}]",
        title="Agent Health Check",
        border_style=status_color
    ))
    
    # Components table
    table = Table(title="Component Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="white")
    
    for component, status in health_status["components"].items():
        color = "green" if status == "operational" else "yellow" if "configured" in status else "red"
        table.add_row(component, f"[{color}]{status}[/{color}]")
    
    console.print(table)


def main():
    """Main CLI entry point."""
    if not typer:
        # Fallback for missing typer
        print("AutoDegen CLI")
        print("Error: CLI dependencies not installed.")
        print("Install with: pip install typer rich")
        print("Or run: pip install 'autodegen[cli]'")
        sys.exit(1)
    
    try:
        app()
    except KeyboardInterrupt:
        if console:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
        else:
            print("\nOperation cancelled by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
