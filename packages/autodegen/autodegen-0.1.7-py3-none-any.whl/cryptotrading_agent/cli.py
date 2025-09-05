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
    from rich import print as rprint
except ImportError:
    typer = None
    Console = None
    rprint = print

from .agent import TradingAgent
from .exceptions import TradingAgentError, ConfigurationError

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
    timeout: float = typer.Option(30.0, "--timeout", help="Request timeout in seconds")
):
    """Analyze a cryptocurrency symbol and get trading insights."""
    if not typer:
        handle_typer_import_error()
    
    async def _analyze():
        try:
            # Initialize agent
            agent = TradingAgent()
            
            if console:
                with console.status(f"[bold green]Analyzing {symbol.upper()}..."):
                    result = await agent.analyze(
                        symbol=symbol.upper(),
                        timeframe=timeframe, 
                        structured=structured,
                        timeout=timeout
                    )
            else:
                print(f"Analyzing {symbol.upper()}...")
                result = await agent.analyze(
                    symbol=symbol.upper(),
                    timeframe=timeframe,
                    structured=structured, 
                    timeout=timeout
                )
            
            # Output results
            if output_format == "json" and structured:
                print(json.dumps(result.dict() if hasattr(result, 'dict') else str(result), indent=2))
            elif output_format == "rich" and console:
                _display_rich_analysis(result, symbol.upper())
            else:
                print(str(result))
                
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


def _display_rich_analysis(result, symbol: str):
    """Display analysis results using rich formatting."""
    if not console:
        return
    
    try:
        if hasattr(result, 'dict'):
            # Structured result
            data = result.dict()
            
            # Title panel
            console.print(Panel(data['title'], title=f"Analysis: {symbol}", border_style="green"))
            
            # Market state
            console.print(Panel(data['market_state'], title="🏢 Market State", border_style="blue"))
            
            # Trend indicators  
            console.print(Panel(data['trend_indicators'], title="📈 Trend Indicators", border_style="cyan"))
            
            # Oscillators
            console.print(Panel(data['oscillators'], title="⚡ Oscillators", border_style="yellow"))
            
            # Volume indicators
            console.print(Panel(data['volume_indicators'], title="📊 Volume Analysis", border_style="purple"))
            
            # Fibonacci levels
            console.print(Panel(data['fibonacci_levels'], title="🎯 Fibonacci Levels", border_style="magenta"))
            
            # Elliott Wave
            console.print(Panel(data['elliott_wave'], title="🌊 Elliott Wave", border_style="bright_blue"))
            
            # Smart Money Concepts
            console.print(Panel(data['smart_money_concepts'], title="💎 Smart Money Concepts", border_style="bright_magenta"))
            
            # Trading setup
            console.print(Panel(data['trading_setup'], title="🎯 Trading Setup", border_style="bright_green"))
            
            # Risk assessment  
            console.print(Panel(data['risk_assessment'], title="⚠️ Risk Assessment", border_style="bright_red"))
            
            # Outlook
            console.print(Panel(data['outlook'], title="🔮 Outlook", border_style="red"))
        else:
            # Text result
            console.print(Panel(Markdown(str(result)), title=f"Analysis: {symbol}", border_style="green"))
    except Exception as e:
        console.print(f"[yellow]Warning: Could not format output: {e}[/yellow]")
        console.print(str(result))


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