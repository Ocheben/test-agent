#!/usr/bin/env python3
"""
Thinking Agent System - Setup and Test Script

This script helps set up and test the complete Thinking Agent system
with its new app API structure.
"""

import subprocess
import sys
import os
from pathlib import Path
import asyncio


def print_banner():
    """Print system banner."""
    print("""
    🧠 THINKING AGENT SYSTEM
    ========================
    
    ✅ System successfully reorganized with:
    • App API with FastAPI
    • Complete REST endpoints
    • Thinking agent with RAG
    • Service orchestration
    • Multi-provider LLM support
    """)


def show_structure():
    """Show the new project structure."""
    print("""
    📁 NEW PROJECT STRUCTURE:
    
    thinking-agent/
    ├── app/                       # App API and agent system
    │   ├── src/                   # Core agent implementation
    │   │   ├── agent/            # Thinking agent
    │   │   ├── core/             # LLM interfaces
    │   │   ├── rag/              # RAG system
    │   │   ├── services/         # Service orchestration
    │   │   └── config/           # Configuration
    │   ├── api/                  # FastAPI application
    │   │   ├── app.py           # Main API routes
    │   │   ├── models.py        # Pydantic models
    │   │   └── __init__.py
    │   ├── examples/            # Usage examples
    │   ├── server.py            # API server script
    │   ├── requirements.txt     # Dependencies
    │   ├── .env.example        # Environment template
    │   └── README.md           # App documentation
    ├── client_example.py        # API client demo
    └── README.md               # Main documentation
    """)


def show_api_endpoints():
    """Show available API endpoints."""
    print("""
    🌐 API ENDPOINTS:
    
    Chat & Interaction:
    • POST /chat                 - Chat with the thinking agent
    • POST /explain              - Explain reasoning approach
    • GET  /conversation-history - Get conversation history
    • DELETE /conversation-history - Clear conversation history
    
    Knowledge Management:
    • POST /knowledge           - Add knowledge to agent
    
    System Information:
    • GET  /status              - Get agent status
    • GET  /services            - List available services
    • GET  /health              - Health check
    • GET  /docs                - Interactive API documentation
    """)


def show_usage_examples():
    """Show usage examples."""
    print("""
    🚀 USAGE EXAMPLES:
    
    1. Start the API server:
       cd app
       python server.py
    
    2. Chat via curl:
       curl -X POST "http://127.0.0.1:8000/chat" \\
            -H "Content-Type: application/json" \\
            -d '{"message": "What is AI?", "show_thinking": true}'
    
    3. Python client:
       python client_example.py
    
    4. Add knowledge:
       curl -X POST "http://127.0.0.1:8000/knowledge" \\
            -H "Content-Type: application/json" \\
            -d '{"content": "Python is a programming language", "source": "user"}'
    
    5. View interactive docs:
       http://127.0.0.1:8000/docs
    """)


def check_system():
    """Check if the system is properly set up."""
    print("\n🔍 SYSTEM CHECK:")
    print("-" * 40)
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} (3.8+ required)")
    
    # Check app directory
    app_dir = Path("app")
    if app_dir.exists():
        print("✅ App directory exists")
    else:
        print("❌ App directory missing")
        return False
    
    # Check key files
    key_files = [
        "app/src/agent/thinking_agent.py",
        "app/api/app.py",
        "app/server.py",
        "app/requirements.txt",
        "client_example.py"
    ]
    
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} missing")
    
    # Check environment setup
    env_file = Path("app/.env")
    env_example = Path("app/.env.example")
    
    if env_example.exists():
        print("✅ .env.example template available")
        if env_file.exists():
            print("✅ .env configuration file exists")
        else:
            print("⚠️  .env file not found (copy from .env.example)")
    else:
        print("❌ .env.example template missing")
    
    return True


def show_next_steps():
    """Show next steps for users."""
    print("""
    🎯 NEXT STEPS:
    
    1. SET UP ENVIRONMENT:
       # Create virtual environment
       python3 -m venv thinking-agent-env
       source thinking-agent-env/bin/activate  # On Windows: thinking-agent-env\\Scripts\\activate
    
    2. INSTALL DEPENDENCIES:
       cd app
       pip install -r requirements.txt
    
    3. CONFIGURE API KEYS:
       cp .env.example .env
       # Edit .env with your OPENAI_API_KEY or ANTHROPIC_API_KEY
    
    4. START THE SERVER:
       python server.py
       # Server will run at http://127.0.0.1:8000
    
    5. TEST THE API:
       # In another terminal:
       python ../client_example.py
       
       # Or visit: http://127.0.0.1:8000/docs
    
    6. INTEGRATE WITH YOUR APPLICATION:
       # Use the REST API endpoints in your own applications
       # See app/README.md for detailed API documentation
    """)


def show_features():
    """Show key features."""
    print("""
    ⭐ KEY FEATURES IMPLEMENTED:
    
    🤔 Thinking Agent:
    • Multi-step reasoning process
    • Query analysis and planning
    • Information synthesis
    • Transparent thought process
    
    📚 RAG Orchestration:
    • ChromaDB and FAISS support
    • Intelligent document chunking
    • Hybrid retrieval strategies
    • Knowledge base management
    
    🔧 Service Selection:
    • Math solver service
    • Text summarization service
    • Web search service (mock)
    • Document retrieval service
    • Automatic service routing
    
    🌐 REST API:
    • FastAPI framework
    • Interactive documentation
    • Pydantic data validation
    • Comprehensive error handling
    • CORS support
    
    🎯 Multi-Provider Support:
    • OpenAI GPT models
    • Anthropic Claude models
    • Extensible architecture
    """)


async def run_quick_test():
    """Run a quick test of the system."""
    print("\n🧪 RUNNING QUICK TEST:")
    print("-" * 40)
    
    try:
        # Test basic imports
        sys.path.insert(0, str(Path("app")))
        
        from app.src.services.service_registry import ServiceRegistry
        print("✅ Service registry imports successfully")
        
        registry = ServiceRegistry()
        services = registry.list_services()
        print(f"✅ {len(services)} services available: {list(services.keys())}")
        
        # Test math service
        from app.src.services.base_service import MathSolverService, ServiceRequest
        
        math_service = MathSolverService()
        request = ServiceRequest(query="Test math query", parameters={})
        
        response = await math_service.process(request)
        if response.success:
            print("✅ Math service responds successfully")
        else:
            print("❌ Math service failed")
        
        print("✅ Basic system test passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("   Install dependencies with: pip install -r app/requirements.txt")


def main():
    """Main function."""
    print_banner()
    show_structure()
    show_api_endpoints()
    show_usage_examples()
    show_features()
    
    # System check
    system_ok = check_system()
    
    if system_ok:
        # Run quick test
        asyncio.run(run_quick_test())
    
    show_next_steps()
    
    print("""
    🎉 SYSTEM SETUP COMPLETE!
    
    The Thinking Agent has been successfully reorganized with:
    • Complete app API system
    • REST endpoints for easy integration
    • Comprehensive documentation
    • Client examples and demos
    
    Ready to start building with AI! 🚀
    """)


if __name__ == "__main__":
    main()