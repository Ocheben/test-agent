#!/usr/bin/env python3
"""
Thinking Agent API Server

Run this script to start the FastAPI server for the Thinking Agent.

Usage:
    python server.py                    # Run with default settings
    python server.py --host 0.0.0.0    # Run on all interfaces
    python server.py --port 8080       # Run on custom port
    python server.py --reload          # Enable auto-reload for development
"""

import argparse
import uvicorn
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables should be set manually.")

def check_dependencies():
    """Check if required dependencies are available."""
    missing_deps = []
    
    try:
        import fastapi
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import uvicorn
    except ImportError:
        missing_deps.append("uvicorn")
    
    try:
        import pydantic
    except ImportError:
        missing_deps.append("pydantic")
    
    if missing_deps:
        print(f"❌ Missing required dependencies: {', '.join(missing_deps)}")
        print("Install them with: pip install " + " ".join(missing_deps))
        return False
    
    return True


def check_api_keys():
    """Check if API keys are configured."""
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        print("⚠️  Warning: No LLM API keys found.")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables")
        print("   or create a .env file with these variables.")
        print("   The agent will use mock responses without API keys.")
        return False
    
    provider = "OpenAI" if openai_key else "Anthropic"
    print(f"✅ {provider} API key found")
    return True


def print_banner():
    """Print server startup banner."""
    print("""
    🧠 THINKING AGENT API SERVER
    ============================
    
    Advanced LLM Agent with:
    • 🤔 Multi-step thinking and reasoning
    • 📚 RAG-powered knowledge retrieval  
    • 🔧 Intelligent service orchestration
    • 💬 Natural conversation interface
    """)


def print_endpoints(host: str, port: int):
    """Print available endpoints."""
    base_url = f"http://{host}:{port}"
    
    print(f"""
    🌐 Server running at: {base_url}
    
    📚 API Documentation:
      • Swagger UI: {base_url}/docs
      • ReDoc: {base_url}/redoc
    
    🔧 Main Endpoints:
      • POST {base_url}/chat          - Chat with the agent
      • POST {base_url}/knowledge     - Add knowledge to agent
      • GET  {base_url}/status        - Get agent status
      • GET  {base_url}/services      - List available services
      • GET  {base_url}/health        - Health check
    
    💡 Example curl request:
      curl -X POST "{base_url}/chat" \\
           -H "Content-Type: application/json" \\
           -d '{{"message": "What is machine learning?", "show_thinking": true}}'
    """)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Thinking Agent API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port", 
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)"
    )
    
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Log level (default: info)"
    )
    
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Skip banner display"
    )
    
    args = parser.parse_args()
    
    # Display banner
    if not args.no_banner:
        print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies and try again.")
        return 1
    
    # Check API keys
    check_api_keys()
    
    # Print endpoint information
    if not args.no_banner:
        print_endpoints(args.host, args.port)
    
    try:
        # Start the server
        uvicorn.run(
            "api.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=1 if args.reload else args.workers,  # Reload doesn't work with multiple workers
            log_level=args.log_level,
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Server failed to start: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())