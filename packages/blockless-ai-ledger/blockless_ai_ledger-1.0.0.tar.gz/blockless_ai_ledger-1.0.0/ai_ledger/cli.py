#!/usr/bin/env python3
"""
AI Ledger CLI - Simple commands for joining and managing the global network.

Provides easy-to-use commands for anyone to join the AI Ledger network.
"""

import asyncio
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional

import typer
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colors
init(autoreset=True)

app = typer.Typer(
    name="ailedger",
    help="🌍 AI Ledger - Join the global decentralized AI-powered network",
    no_args_is_help=True,
    add_completion=False
)


def print_header():
    """Print the AI Ledger header."""
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("=" * 60)
    print("  🌍 AI LEDGER - Global Decentralized Network")
    print("  🤖 AI-Powered • 🔒 Secure • 🌐 Worldwide")
    print("=" * 60)
    print(f"{Style.RESET_ALL}")


def print_success(message: str):
    """Print success message."""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message."""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print info message."""
    print(f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")


@app.command()
def join(
    openai_key: Optional[str] = typer.Option(None, "--openai-key", help="Your OpenAI API key for real AI validation"),
    port: int = typer.Option(8001, "--port", help="Port to run on"),
    validators: int = typer.Option(2, "--validators", help="Number of validators to run"),
    demo: bool = typer.Option(False, "--demo", help="Run in demo mode (no OpenAI key required)"),
    network: str = typer.Option("ailedger-mainnet", "--network", help="Network to join"),
    node_name: str = typer.Option("", "--name", help="Human-readable node name")
):
    """
    🌍 Join the global AI Ledger network instantly.
    
    This command starts a node that automatically connects to the worldwide
    AI Ledger network using decentralized discovery protocols.
    """
    print_header()
    
    print_info("Joining the global AI Ledger network...")
    print()
    
    # Configuration
    if demo or not openai_key:
        if not demo:
            print_warning("No OpenAI API key provided - using demo mode")
            print_info("For real AI validation, use: ailedger join --openai-key YOUR_KEY")
        
        os.environ["LLM_MODE"] = "stub"
        print_info("Mode: Demo (deterministic AI simulation)")
    else:
        os.environ["OPENAI_API_KEY"] = openai_key
        os.environ["LLM_MODE"] = "openai"
        print_success("Mode: Production (real OpenAI AI validation)")
    
    # Set environment
    os.environ["AI_LEDGER_LOG_LEVEL"] = "INFO"
    
    if not node_name:
        import socket
        node_name = f"ailedger-{socket.gethostname()}-{int(time.time() % 10000)}"
    
    print()
    print_info("Configuration:")
    print(f"  • Network: {network}")
    print(f"  • Port: {port}")
    print(f"  • Validators: {validators}")
    print(f"  • Node Name: {node_name}")
    print(f"  • AI Mode: {os.environ.get('LLM_MODE', 'stub')}")
    
    print()
    print_info("Starting node...")
    print_warning("Press Ctrl+C to stop")
    
    try:
        # Import and run network node
        from .network_node import main as node_main
        
        # Set up command line args for network node
        sys.argv = [
            "ailedger-node",
            "run",
            "--port", str(port),
            "--host", "0.0.0.0",
            "--validators", str(validators),
            "--node-name", node_name,
            "--log-level", "INFO"
        ]
        
        # Run the node
        node_main()
        
    except KeyboardInterrupt:
        print()
        print_info("Stopping node...")
        print_success("Node stopped. Thanks for participating in the AI Ledger network!")
    except Exception as e:
        print_error(f"Failed to start node: {e}")
        print_info("Try running with --demo flag for testing")
        sys.exit(1)


@app.command("demo")
def run_demo():
    """Run the interactive demo."""
    try:
        from .demo import main as demo_main
        demo_main()
    except ImportError as e:
        print(f"❌ Demo not available: {e}")


@app.command("test")
def run_tests():
    """Run the test suite."""
    try:
        import pytest
        pytest.main(["-v"])
    except ImportError:
        print("❌ pytest not installed. Install with: pip install pytest")


@app.command("version")
def show_version():
    """Show version information."""
    try:
        from . import __version__
        print(f"AI Ledger v{__version__}")
    except ImportError:
        print("AI Ledger v0.1.0")


@app.command("doctor")
def health_check():
    """Check system health and requirements."""
    print("🏥 AI Ledger Health Check")
    print("=" * 30)
    
    # Check Python version
    import sys
    python_version = sys.version_info
    if python_version >= (3, 11):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (need 3.11+)")
    
    # Check OpenAI key
    if os.getenv("OPENAI_API_KEY"):
        print("✅ OpenAI API key detected")
    else:
        print("⚠️  No OpenAI API key (will use demo mode)")
    
    # Check network connectivity
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), 1)
        print("✅ Network connectivity")
    except OSError:
        print("❌ No network connectivity")
    
    # Check ports
    def check_port(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    if check_port(8001):
        print("✅ Port 8001 available")
    else:
        print("⚠️  Port 8001 in use (will auto-select another)")
    
    print("\n🎯 Ready to join the network!")
    print("Run: ailedger join")


def main():
    """Main CLI entry point."""
    if len(sys.argv) == 1:
        # No arguments - show quick start
        print("🚀 AI Ledger - Quick Start")
        print("=" * 30)
        print()
        print("Join the network instantly:")
        print("  ailedger join")
        print()
        print("With your OpenAI key:")
        print("  ailedger join --openai-key your-key-here")
        print()
        print("Demo mode (no API key needed):")
        print("  ailedger join --demo")
        print()
        print("Other commands:")
        print("  ailedger demo      - Interactive demo")
        print("  ailedger doctor    - Health check")
        print("  ailedger --help    - Full help")
        print()
        return
    
    app()


if __name__ == "__main__":
    main()