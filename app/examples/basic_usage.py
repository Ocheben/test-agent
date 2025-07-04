"""
Basic usage example of the Thinking Agent with RAG and service orchestration.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the agent components
from src.agent.thinking_agent import ThinkingAgent
from src.core.base_llm import create_llm
from src.rag.retriever import RAGOrchestrator
from src.services.service_registry import ServiceRegistry


async def basic_example():
    """Basic example showing agent capabilities."""
    
    print("🤖 Initializing Thinking Agent...")
    
    # Create the agent
    agent = ThinkingAgent()
    
    # Add some knowledge to the RAG system
    print("📚 Adding knowledge to the system...")
    
    knowledge_items = [
        {
            "content": """
            Python is a high-level, interpreted programming language with dynamic semantics. 
            Its high-level built-in data structures, combined with dynamic typing and dynamic binding, 
            make it very attractive for Rapid Application Development, as well as for use as a scripting 
            or glue language to connect existing components together.
            """,
            "source": "python_info",
            "metadata": {"topic": "programming", "language": "python"}
        },
        {
            "content": """
            Machine Learning is a subset of artificial intelligence (AI) that focuses on algorithms 
            that can learn and make decisions or predictions based on data. It includes supervised learning, 
            unsupervised learning, and reinforcement learning approaches.
            """,
            "source": "ml_info", 
            "metadata": {"topic": "ai", "field": "machine learning"}
        },
        {
            "content": """
            Climate change refers to long-term shifts in global or regional climate patterns. 
            It has been largely attributed to increased levels of atmospheric carbon dioxide 
            produced by the use of fossil fuels since the mid-20th century.
            """,
            "source": "climate_info",
            "metadata": {"topic": "environment", "field": "climate science"}
        }
    ]
    
    for item in knowledge_items:
        await agent.add_knowledge(
            content=item["content"],
            source=item["source"], 
            metadata=item["metadata"]
        )
    
    print("✅ Knowledge added successfully!")
    
    # Test queries
    test_queries = [
        "What is Python and why is it popular for development?",
        "Calculate 15 * 23 + 47",
        "Explain machine learning in simple terms",
        "Summarize the key points about climate change",
        "What are the current trends in artificial intelligence?"
    ]
    
    print("\n" + "="*60)
    print("🧠 TESTING THINKING AGENT")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 50)
        
        try:
            # Process the query
            response = await agent.process_query(query)
            
            # Display results
            print(f"📋 Final Answer:")
            print(response.final_answer)
            
            print(f"\n📊 Metadata:")
            print(f"  • Services used: {response.services_used}")
            print(f"  • RAG context used: {response.rag_context_used}")
            print(f"  • Processing time: {response.total_time:.2f}s")
            print(f"  • Thinking steps: {len(response.thinking_steps)}")
            
            # Show thinking process (abbreviated)
            print(f"\n🤔 Thinking Process:")
            for step in response.thinking_steps:
                print(f"  Step {step.step_number}: {step.thought}")
                print(f"    Reasoning: {step.reasoning[:100]}{'...' if len(step.reasoning) > 100 else ''}")
                if step.action:
                    print(f"    Action: {step.action}")
                
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
        
        print("\n" + "="*60)


async def service_testing():
    """Test individual services."""
    
    print("\n🔧 TESTING INDIVIDUAL SERVICES")
    print("="*60)
    
    agent = ThinkingAgent()
    registry = agent.service_registry
    
    # Test each service type
    service_tests = [
        ("MathSolverService", "Calculate 25 * 4 + 10 - 5"),
        ("WebSearchService", "Find information about Python programming"),
        ("TextSummarizationService", """
        Artificial intelligence (AI) is intelligence demonstrated by machines, 
        in contrast to the natural intelligence displayed by humans and animals. 
        Leading AI textbooks define the field as the study of "intelligent agents": 
        any device that perceives its environment and takes actions that maximize 
        its chance of successfully achieving its goals. Colloquially, the term 
        "artificial intelligence" is often used to describe machines that mimic 
        "cognitive" functions that humans associate with the human mind, such as 
        "learning" and "problem solving".
        """)
    ]
    
    for service_name, test_query in service_tests:
        print(f"\n🔍 Testing {service_name}")
        print(f"Query: {test_query}")
        print("-" * 40)
        
        try:
            from src.services.base_service import ServiceRequest
            
            request = ServiceRequest(
                query=test_query,
                parameters={},
                context={"test": True}
            )
            
            response = await registry.route_request(request, service_name)
            
            if response.success:
                print(f"✅ Success:")
                print(response.content[:300] + "..." if len(response.content) > 300 else response.content)
                print(f"Metadata: {response.metadata}")
            else:
                print(f"❌ Failed: {response.error_message}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def rag_testing():
    """Test RAG functionality."""
    
    print("\n📚 TESTING RAG FUNCTIONALITY")
    print("="*60)
    
    # Create RAG orchestrator
    rag = RAGOrchestrator()
    
    # Add some documents
    documents = [
        "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France.",
        "The Great Wall of China is a series of fortifications made of stone, brick, tamped earth, and wood.",
        "Machu Picchu is an ancient Inca city located in the Andes Mountains of Peru.",
        "The Colosseum is an oval amphitheatre in the centre of Rome, Italy."
    ]
    
    print("Adding documents to knowledge base...")
    for i, doc in enumerate(documents):
        await rag.add_knowledge(
            content=doc,
            source="landmarks",
            metadata={"type": "landmark", "id": i}
        )
    
    # Test queries
    test_queries = [
        "Tell me about the Eiffel Tower",
        "What do you know about ancient structures?",
        "Where is Machu Picchu located?",
        "What landmarks are in Europe?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 40)
        
        try:
            result = await rag.query_knowledge(query, use_hybrid=True, k=3)
            context = await rag.get_context_for_query(query)
            
            print(f"Found {result.total_found} documents in {result.retrieval_time:.3f}s")
            print(f"Context:\n{context[:200]}{'...' if len(context) > 200 else ''}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Show stats
    print(f"\n📊 Knowledge Base Stats:")
    stats = rag.get_knowledge_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


async def main():
    """Main execution function."""
    
    print("🚀 Starting Thinking Agent Demo")
    print("="*60)
    
    # Check for API keys
    if not (os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")):
        print("⚠️  Warning: No API keys found. Using mock responses.")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables for full functionality.\n")
    
    try:
        # Run all examples
        await basic_example()
        await service_testing()
        await rag_testing()
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())