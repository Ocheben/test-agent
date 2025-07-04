#!/usr/bin/env python3
"""
Thinking Agent API Client Example

This script demonstrates how to interact with the Thinking Agent API
using HTTP requests. It shows examples of all major endpoints.
"""

import asyncio
import json
import httpx
import time
from typing import Dict, Any, Optional


class ThinkingAgentClient:
    """Client for interacting with the Thinking Agent API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = None
    
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=60.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the API server is healthy."""
        response = await self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    async def chat(
        self, 
        message: str, 
        show_thinking: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a chat message to the thinking agent."""
        payload = {
            "message": message,
            "show_thinking": show_thinking,
            "use_rag": True
        }
        
        if context:
            payload["context"] = context
        
        response = await self.session.post(
            f"{self.base_url}/chat",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def add_knowledge(
        self, 
        content: str, 
        source: str = "client",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add knowledge to the agent's knowledge base."""
        payload = {
            "content": content,
            "source": source
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        response = await self.session.post(
            f"{self.base_url}/knowledge",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the agent's current status."""
        response = await self.session.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.json()
    
    async def list_services(self) -> Dict[str, Any]:
        """List all available services."""
        response = await self.session.get(f"{self.base_url}/services")
        response.raise_for_status()
        return response.json()
    
    async def explain_reasoning(self, message: str) -> Dict[str, Any]:
        """Get explanation of how the agent would approach a query."""
        payload = {"message": message}
        
        response = await self.session.post(
            f"{self.base_url}/explain",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def get_conversation_history(self) -> Dict[str, Any]:
        """Get the agent's conversation history."""
        response = await self.session.get(f"{self.base_url}/conversation-history")
        response.raise_for_status()
        return response.json()
    
    async def clear_conversation_history(self) -> Dict[str, Any]:
        """Clear the agent's conversation history."""
        response = await self.session.delete(f"{self.base_url}/conversation-history")
        response.raise_for_status()
        return response.json()


async def demo_basic_chat():
    """Demonstrate basic chat functionality."""
    print("🗣️  BASIC CHAT DEMO")
    print("=" * 50)
    
    async with ThinkingAgentClient() as client:
        # Test questions
        questions = [
            "What is 15 * 23 + 47?",
            "What is machine learning?",
            "Can you summarize this text: Artificial intelligence is transforming how we work and live. It enables machines to perform tasks that traditionally required human intelligence.",
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n📝 Question {i}: {question}")
            print("-" * 40)
            
            try:
                response = await client.chat(question, show_thinking=True)
                
                print(f"🤖 Answer: {response['answer']}")
                print(f"⚡ Processing time: {response['processing_time']:.2f}s")
                print(f"🔧 Services used: {', '.join(response['services_used'])}")
                
                if response.get('thinking_steps'):
                    print(f"🤔 Thinking steps:")
                    for step in response['thinking_steps']:
                        print(f"  Step {step['step_number']}: {step['thought']}")
                        print(f"    {step['reasoning'][:100]}{'...' if len(step['reasoning']) > 100 else ''}")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")


async def demo_knowledge_management():
    """Demonstrate knowledge management features."""
    print("\n📚 KNOWLEDGE MANAGEMENT DEMO")
    print("=" * 50)
    
    async with ThinkingAgentClient() as client:
        # Add some knowledge
        knowledge_items = [
            {
                "content": "The Eiffel Tower is located in Paris, France and was completed in 1889.",
                "metadata": {"topic": "landmarks", "location": "france"}
            },
            {
                "content": "Python was created by Guido van Rossum and first released in 1991.",
                "metadata": {"topic": "programming", "language": "python"}
            }
        ]
        
        print("📝 Adding knowledge to the agent...")
        for item in knowledge_items:
            try:
                result = await client.add_knowledge(
                    content=item["content"],
                    source="demo",
                    metadata=item["metadata"]
                )
                print(f"✅ Added: {item['content'][:50]}...")
                
            except Exception as e:
                print(f"❌ Failed to add knowledge: {str(e)}")
        
        # Test knowledge retrieval
        print(f"\n🔍 Testing knowledge retrieval...")
        test_questions = [
            "Tell me about the Eiffel Tower",
            "Who created Python programming language?"
        ]
        
        for question in test_questions:
            try:
                response = await client.chat(question, show_thinking=False)
                print(f"\n❓ {question}")
                print(f"🤖 {response['answer']}")
                print(f"📚 Used RAG: {response['rag_context_used']}")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")


async def demo_agent_status():
    """Demonstrate agent status and service information."""
    print("\n📊 AGENT STATUS DEMO")
    print("=" * 50)
    
    async with ThinkingAgentClient() as client:
        try:
            # Get agent status
            status = await client.get_status()
            
            print("🤖 Agent Status:")
            print(f"  Status: {status['status']}")
            print(f"  Available services: {len(status['available_services'])}")
            print(f"  Knowledge base documents: {status['knowledge_base_stats'].get('total_documents', 0)}")
            
            # List services
            services = await client.list_services()
            
            print(f"\n🔧 Available Services ({services['total_count']}):")
            for name, info in services['services'].items():
                print(f"  • {name}: {info['description']}")
            
            # Get conversation history
            history = await client.get_conversation_history()
            
            print(f"\n💬 Conversation History:")
            print(f"  Total exchanges: {history['total_exchanges']}")
            print(f"  Recent messages: {len(history['history'])}")
            
        except Exception as e:
            print(f"❌ Error getting status: {str(e)}")


async def demo_reasoning_explanation():
    """Demonstrate reasoning explanation feature."""
    print("\n🧠 REASONING EXPLANATION DEMO")
    print("=" * 50)
    
    async with ThinkingAgentClient() as client:
        test_query = "How would you solve a complex mathematical word problem?"
        
        try:
            explanation = await client.explain_reasoning(test_query)
            
            print(f"❓ Query: {explanation['query']}")
            print(f"🧠 Reasoning Explanation:")
            print(explanation['explanation'])
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def interactive_chat():
    """Interactive chat session with the agent."""
    print("\n💬 INTERACTIVE CHAT")
    print("=" * 50)
    print("Type 'quit' to exit, 'clear' to clear history")
    
    async with ThinkingAgentClient() as client:
        # Check if server is running
        try:
            health = await client.health_check()
            if health['status'] != 'healthy':
                print("❌ API server is not healthy")
                return
        except Exception as e:
            print(f"❌ Cannot connect to API server: {str(e)}")
            print("Make sure the server is running with: python app/server.py")
            return
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    break
                elif user_input.lower() == 'clear':
                    await client.clear_conversation_history()
                    print("🗑️  Conversation history cleared")
                    continue
                elif user_input.lower() == 'status':
                    status = await client.get_status()
                    print(f"📊 Agent Status: {status['status']}")
                    continue
                elif not user_input:
                    continue
                
                # Send message to agent
                response = await client.chat(user_input, show_thinking=False)
                
                print(f"🤖 Agent: {response['answer']}")
                print(f"⚡ ({response['processing_time']:.1f}s, services: {', '.join(response['services_used']) or 'none'})")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        print("\n👋 Chat ended")


async def main():
    """Main demo function."""
    print("🧠 THINKING AGENT API CLIENT DEMO")
    print("=" * 60)
    
    # Check if server is running
    async with ThinkingAgentClient() as client:
        try:
            health = await client.health_check()
            print(f"✅ API server is running and {health['status']}")
        except Exception as e:
            print(f"❌ Cannot connect to API server: {str(e)}")
            print("\n🚀 To start the server, run:")
            print("   cd app")
            print("   python server.py")
            print("\nThen run this demo again.")
            return
    
    try:
        # Run demos
        await demo_basic_chat()
        await demo_knowledge_management()
        await demo_agent_status()
        await demo_reasoning_explanation()
        
        # Interactive chat
        print(f"\n🎯 Ready for interactive chat!")
        await interactive_chat()
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")


if __name__ == "__main__":
    # Check if httpx is available
    try:
        import httpx
    except ImportError:
        print("❌ httpx library not found. Install it with:")
        print("   pip install httpx")
        exit(1)
    
    asyncio.run(main())