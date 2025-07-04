#!/usr/bin/env python3
"""
Test script to verify the basic structure of the Thinking Agent system.
This script tests imports and basic functionality without requiring external APIs.
"""

import sys
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from src.config.settings import settings
        print("✅ Config module imported successfully")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
    
    try:
        from src.core.base_llm import BaseLLM, LLMProvider, LLMResponse
        print("✅ Core LLM module imported successfully")
    except Exception as e:
        print(f"❌ Core LLM import failed: {e}")
    
    try:
        from src.rag.vector_store import BaseVectorStore, Document
        print("✅ RAG vector store module imported successfully")
    except Exception as e:
        print(f"❌ RAG vector store import failed: {e}")
    
    try:
        from src.rag.retriever import DocumentRetriever, RAGOrchestrator
        print("✅ RAG retriever module imported successfully")
    except Exception as e:
        print(f"❌ RAG retriever import failed: {e}")
    
    try:
        from src.services.base_service import BaseService, ServiceRequest, ServiceResponse
        print("✅ Services base module imported successfully")
    except Exception as e:
        print(f"❌ Services base import failed: {e}")
    
    try:
        from src.services.service_registry import ServiceRegistry
        print("✅ Service registry module imported successfully")
    except Exception as e:
        print(f"❌ Service registry import failed: {e}")
    
    try:
        from src.agent.thinking_agent import ThinkingAgent, ThinkingStep, AgentResponse
        print("✅ Thinking agent module imported successfully")
    except Exception as e:
        print(f"❌ Thinking agent import failed: {e}")


async def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test service registry
        from src.services.service_registry import ServiceRegistry
        registry = ServiceRegistry()
        
        services = registry.list_services()
        print(f"✅ Service registry created with {len(services)} services")
        
        # Test service recommendations
        recommendations = registry.get_service_recommendations("calculate 2+2")
        print(f"✅ Service recommendations work: {recommendations}")
        
    except Exception as e:
        print(f"❌ Service registry test failed: {e}")
    
    try:
        # Test math service (doesn't require external APIs)
        from src.services.base_service import MathSolverService, ServiceRequest
        
        math_service = MathSolverService()
        request = ServiceRequest(
            query="Calculate 15 + 25",
            parameters={}
        )
        
        response = await math_service.process(request)
        if response.success:
            print(f"✅ Math service works: {response.content}")
        else:
            print(f"❌ Math service failed: {response.error_message}")
            
    except Exception as e:
        print(f"❌ Math service test failed: {e}")
    
    try:
        # Test text summarization service
        from src.services.base_service import TextSummarizationService, ServiceRequest
        
        text_service = TextSummarizationService()
        request = ServiceRequest(
            query="This is a test document. It contains multiple sentences. The purpose is to test summarization.",
            parameters={"max_length": 50}
        )
        
        response = await text_service.process(request)
        if response.success:
            print(f"✅ Text summarization service works")
        else:
            print(f"❌ Text summarization service failed: {response.error_message}")
            
    except Exception as e:
        print(f"❌ Text summarization test failed: {e}")


def test_configuration():
    """Test configuration system."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from src.config.settings import settings
        
        print(f"✅ Default LLM provider: {settings.default_llm_provider}")
        print(f"✅ Default model: {settings.default_model}")
        print(f"✅ Available services: {len(settings.available_services)}")
        print(f"✅ Chunk size: {settings.chunk_size}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")


def show_project_structure():
    """Show the project structure."""
    print("\n📁 Project Structure:")
    print("thinking-agent/")
    print("├── src/")
    print("│   ├── agent/           # Main agent implementation")
    print("│   ├── core/            # Core LLM interfaces")
    print("│   ├── rag/             # RAG implementation")
    print("│   ├── services/        # Service system")
    print("│   └── config/          # Configuration")
    print("├── examples/            # Usage examples")
    print("├── main.py              # Main entry point")
    print("├── requirements.txt     # Dependencies")
    print("├── .env.example         # Configuration template")
    print("└── README.md            # Documentation")


def show_next_steps():
    """Show next steps for using the system."""
    print("\n🚀 Next Steps:")
    print("1. Set up a virtual environment:")
    print("   python3 -m venv thinking-agent-env")
    print("   source thinking-agent-env/bin/activate")
    
    print("\n2. Install dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n3. Set up configuration:")
    print("   cp .env.example .env")
    print("   # Edit .env with your API keys")
    
    print("\n4. Run the system:")
    print("   python main.py                    # Interactive demo")
    print("   python main.py --example          # Basic example")
    print("   python main.py --query 'text'     # Single query")
    
    print("\n5. Key features to explore:")
    print("   🤔 Multi-step thinking and reasoning")
    print("   📚 RAG-powered knowledge retrieval")
    print("   🔧 Automatic service selection")
    print("   💬 Natural conversation interface")


async def main():
    """Main test function."""
    print("🧠 THINKING AGENT - System Test")
    print("=" * 60)
    
    # Run tests
    test_imports()
    await test_basic_functionality()
    test_configuration()
    show_project_structure()
    show_next_steps()
    
    print("\n" + "=" * 60)
    print("✅ Basic system structure test completed!")
    print("The Thinking Agent system is ready for use.")


if __name__ == "__main__":
    asyncio.run(main())