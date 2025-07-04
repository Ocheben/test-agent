#!/usr/bin/env python3
"""
Thinking Agent - Main Entry Point

An advanced LLM agent with thinking capabilities, agentic RAG orchestration,
and intelligent service selection.

Usage:
    python main.py                    # Run interactive demo
    python main.py --example          # Run basic example
    python main.py --query "text"     # Process single query
    python main.py --help             # Show help
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Create a .env file manually if needed.")

from src.agent.thinking_agent import ThinkingAgent


async def run_single_query(query: str):
    """Run a single query and display results."""
    
    print(f"🔍 Processing query: {query}")
    print("="*60)
    
    try:
        # Initialize agent
        agent = ThinkingAgent()
        
        # Add some basic knowledge
        await agent.add_knowledge("""
        This is a demonstration of the Thinking Agent system. The agent can:
        1. Think through problems step by step
        2. Use RAG to retrieve relevant information
        3. Select and orchestrate appropriate services
        4. Provide comprehensive, well-reasoned answers
        """, source="system_demo")
        
        # Process query
        response = await agent.process_query(query)
        
        # Display results
        print("\n🤔 THINKING PROCESS:")
        for step in response.thinking_steps:
            print(f"\nStep {step.step_number}: {step.thought}")
            print(f"Reasoning: {step.reasoning[:300]}{'...' if len(step.reasoning) > 300 else ''}")
            if step.action:
                print(f"Action: {step.action}")
        
        print(f"\n💬 FINAL ANSWER:")
        print(response.final_answer)
        
        print(f"\n📊 METADATA:")
        print(f"Services used: {response.services_used}")
        print(f"RAG context used: {response.rag_context_used}")
        print(f"Processing time: {response.total_time:.2f}s")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def run_basic_example():
    """Run the basic example."""
    try:
        from examples.basic_usage import main as basic_main
        await basic_main()
    except ImportError:
        print("❌ Basic example not found. Make sure examples/basic_usage.py exists.")
    except Exception as e:
        print(f"❌ Error running basic example: {str(e)}")


async def run_interactive_demo():
    """Run the interactive demo."""
    try:
        from examples.interactive_demo import main as demo_main
        await demo_main()
    except ImportError:
        print("❌ Interactive demo not found. Make sure examples/interactive_demo.py exists.")
    except Exception as e:
        print(f"❌ Error running interactive demo: {str(e)}")


def check_dependencies():
    """Check if required dependencies are available."""
    missing_deps = []
    
    try:
        import openai
    except ImportError:
        missing_deps.append("openai")
    
    try:
        import anthropic
    except ImportError:
        missing_deps.append("anthropic")
    
    # Check if at least one LLM provider is available
    if "openai" in missing_deps and "anthropic" in missing_deps:
        print("⚠️  Warning: No LLM providers available. Install at least one:")
        print("   pip install openai  # For OpenAI GPT models")
        print("   pip install anthropic  # For Anthropic Claude models")
    
    # Check for other important dependencies
    optional_deps = []
    
    try:
        import chromadb
    except ImportError:
        optional_deps.append("chromadb")
    
    try:
        import sentence_transformers
    except ImportError:
        optional_deps.append("sentence-transformers")
    
    if optional_deps:
        print(f"⚠️  Optional dependencies missing: {', '.join(optional_deps)}")
        print("   Install with: pip install " + " ".join(optional_deps))
    
    # Check API keys
    api_keys_available = bool(os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))
    if not api_keys_available:
        print("⚠️  No API keys found. Set environment variables:")
        print("   export OPENAI_API_KEY=your_key_here")
        print("   export ANTHROPIC_API_KEY=your_key_here")
        print("   Or create a .env file with these variables")
    
    return len(missing_deps) == 0 or len(missing_deps) < 2  # At least one LLM provider


def create_sample_env():
    """Create a sample .env file."""
    env_content = """# Thinking Agent Configuration
# Set your API keys here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Configuration  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Agent Settings (optional)
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4
THINKING_TEMPERATURE=0.7
RESPONSE_TEMPERATURE=0.3
MAX_TOKENS=2000

# RAG Settings (optional)
VECTOR_STORE_PATH=./data/vector_store
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    print("📄 Created .env.example file. Copy it to .env and add your API keys.")


def print_banner():
    """Print the application banner."""
    print("""
    ████████╗██╗  ██╗██╗███╗   ██╗██╗  ██╗██╗███╗   ██╗ ██████╗ 
    ╚══██╔══╝██║  ██║██║████╗  ██║██║ ██╔╝██║████╗  ██║██╔════╝ 
       ██║   ███████║██║██╔██╗ ██║█████╔╝ ██║██╔██╗ ██║██║  ███╗
       ██║   ██╔══██║██║██║╚██╗██║██╔═██╗ ██║██║╚██╗██║██║   ██║
       ██║   ██║  ██║██║██║ ╚████║██║  ██╗██║██║ ╚████║╚██████╔╝
       ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
                                                                  
     █████╗  ██████╗ ███████╗███╗   ██╗████████╗                
    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝                
    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║                   
    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║                   
    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║                   
    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝                   
    
    🧠 Advanced LLM Agent with Thinking, RAG & Service Orchestration
    """)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Thinking Agent - Advanced LLM Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Interactive demo
  python main.py --query "What is machine learning?" # Single query
  python main.py --example                          # Run basic example
  python main.py --setup                            # Create sample config
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        type=str,
        help="Process a single query"
    )
    
    parser.add_argument(
        "--example", "-e",
        action="store_true",
        help="Run basic usage example"
    )
    
    parser.add_argument(
        "--setup", "-s",
        action="store_true",
        help="Create sample configuration files"
    )
    
    parser.add_argument(
        "--check-deps",
        action="store_true", 
        help="Check dependencies and configuration"
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
    
    # Handle setup
    if args.setup:
        create_sample_env()
        return
    
    # Check dependencies
    if args.check_deps:
        print("🔍 Checking dependencies and configuration...")
        deps_ok = check_dependencies()
        if deps_ok:
            print("✅ All critical dependencies are available!")
        else:
            print("❌ Some critical dependencies are missing.")
        return
    
    # Check dependencies automatically
    if not check_dependencies():
        print("\n⚠️  Some dependencies are missing. Run with --check-deps for details.")
        print("You can still use the agent with available providers.\n")
    
    # Handle different modes
    if args.query:
        asyncio.run(run_single_query(args.query))
    elif args.example:
        asyncio.run(run_basic_example())
    else:
        # Default to interactive demo
        print("🚀 Starting interactive demo...")
        asyncio.run(run_interactive_demo())


if __name__ == "__main__":
    main()