"""
Command-line interface for AI Ledger - the main entry point after pip install.
"""

import os
import sys
import subprocess
from pathlib import Path
import typer
from typing import Optional

app = typer.Typer(
    name="blockless",
    help="Blockless AI Ledger - Distributed AI-validated ledger system",
    add_completion=False
)

@app.command("join")
def join_network(
    openai_key: Optional[str] = typer.Option(None, "--openai-key", help="OpenAI API key for real AI validation"),
    port: int = typer.Option(0, "--port", help="Port to run on (auto-generated if 0)"),
    name: Optional[str] = typer.Option(None, "--name", help="Node name (auto-generated if not provided)"),
    bootstrap: Optional[str] = typer.Option(None, "--bootstrap", help="Bootstrap node URL"),
    demo_mode: bool = typer.Option(False, "--demo", help="Run in demo mode (no real AI)")
):
    """Join the AI Ledger network instantly."""
    
    print("🚀 AI Ledger Network - Instant Join")
    print("=" * 40)
    
    # Set up environment
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
        os.environ["LLM_MODE"] = "openai"
        print("✅ Using OpenAI for real AI validation")
    elif demo_mode or not os.getenv("OPENAI_API_KEY"):
        os.environ["LLM_MODE"] = "stub"
        print("🎭 Using demo mode (stub validation)")
        if not demo_mode:
            print("💡 Set --openai-key for real AI validation")
    
    # Auto-generate port
    if port == 0:
        import random
        port = random.randint(8001, 8999)
    
    # Auto-generate name
    if not name:
        import getpass
        import time
        name = f"ailedger-{getpass.getuser()}-{int(time.time()) % 10000}"
    
    print(f"📋 Node: {name}")
    print(f"🔌 Port: {port}")
    print(f"🤖 AI Mode: {os.getenv('LLM_MODE', 'stub')}")
    print()
    
    # Import and run network node
    try:
        from .network_node import NetworkNodeConfig, initialize_network_node, network_app
        import uvicorn
        import asyncio
        
        # Create config
        config = NetworkNodeConfig(
            port=port,
            host="0.0.0.0",
            bootstrap_nodes=[bootstrap] if bootstrap else [],
            validator_count=2,
            node_id=None  # Will be auto-generated
        )
        
        # Add startup handler
        async def startup():
            await initialize_network_node(config)
        
        network_app.add_event_handler("startup", startup)
        
        print("🎉 Starting your AI Ledger node...")
        print(f"📊 Dashboard: http://localhost:{port}/docs")
        print(f"🌐 Network Stats: http://localhost:{port}/network/stats")
        print()
        print("Press Ctrl+C to stop")
        print()
        
        # Run the server
        uvicorn.run(
            "ai_ledger.network_node:network_app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Node stopped. Thanks for participating!")
    except ImportError as e:
        print(f"❌ Installation issue: {e}")
        print("Try: pip install --upgrade ai-ledger")
    except Exception as e:
        print(f"❌ Error starting node: {e}")


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