"""
Interactive demo of the Thinking Agent.
Run this script to have a conversation with the agent.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.agent.thinking_agent import ThinkingAgent


class InteractiveDemo:
    """Interactive demo interface for the thinking agent."""
    
    def __init__(self):
        self.agent = None
        self.show_thinking = True
        self.show_services = True
    
    async def initialize_agent(self):
        """Initialize the thinking agent."""
        print("🤖 Initializing Thinking Agent...")
        
        try:
            self.agent = ThinkingAgent()
            
            # Add some default knowledge
            await self._add_default_knowledge()
            
            print("✅ Agent initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize agent: {str(e)}")
            return False
    
    async def _add_default_knowledge(self):
        """Add some default knowledge to the agent."""
        
        knowledge_items = [
            {
                "content": """
                The Thinking Agent is an advanced AI system that combines multiple capabilities:
                1. Thinking and reasoning through complex problems step by step
                2. RAG (Retrieval Augmented Generation) for accessing knowledge bases
                3. Service orchestration to select and use appropriate tools
                4. Multi-step problem solving with transparent reasoning
                """,
                "source": "system_info"
            },
            {
                "content": """
                Available services include:
                - MathSolverService: For mathematical calculations and equations
                - WebSearchService: For finding current information (mock implementation)
                - TextSummarizationService: For summarizing and analyzing text
                - DocumentRetrievalService: For querying the knowledge base
                """,
                "source": "services_info"
            }
        ]
        
        for item in knowledge_items:
            await self.agent.add_knowledge(
                content=item["content"],
                source=item["source"]
            )
    
    def display_banner(self):
        """Display the welcome banner."""
        print("\n" + "="*80)
        print("🧠 THINKING AGENT - Interactive Demo")
        print("="*80)
        print("Welcome to the Thinking Agent interactive demo!")
        print("\nFeatures:")
        print("  🤔 Step-by-step reasoning and thinking")
        print("  📚 RAG-powered knowledge retrieval")
        print("  🔧 Automatic service selection and orchestration")
        print("  💬 Natural conversation interface")
        print("\nCommands:")
        print("  /help     - Show this help message")
        print("  /thinking - Toggle thinking process display")
        print("  /services - Toggle services usage display")
        print("  /explain  - Explain reasoning for a query without executing")
        print("  /add      - Add knowledge to the system")
        print("  /stats    - Show knowledge base statistics")
        print("  /history  - Show conversation history")
        print("  /clear    - Clear conversation history")
        print("  /quit     - Exit the demo")
        print("="*80)
    
    def display_help(self):
        """Display help information."""
        print("\n📖 HELP")
        print("-" * 40)
        print("This is an interactive demo of the Thinking Agent.")
        print("\nHow it works:")
        print("1. Enter any question or request")
        print("2. The agent will think through the problem step by step")
        print("3. It will gather information from its knowledge base and services")
        print("4. It will provide a comprehensive answer")
        print("\nExample queries:")
        print("  • 'Calculate 15 * 23 + 47'")
        print("  • 'What is the Thinking Agent?'")
        print("  • 'Summarize this text: [your text]'")
        print("  • 'Explain machine learning'")
        print("\nToggle settings:")
        print(f"  • Thinking display: {'ON' if self.show_thinking else 'OFF'}")
        print(f"  • Services display: {'ON' if self.show_services else 'OFF'}")
    
    async def handle_command(self, user_input: str) -> bool:
        """Handle special commands. Returns True if command was handled."""
        
        command = user_input.strip().lower()
        
        if command == "/help":
            self.display_help()
            return True
            
        elif command == "/thinking":
            self.show_thinking = not self.show_thinking
            print(f"🤔 Thinking process display: {'ON' if self.show_thinking else 'OFF'}")
            return True
            
        elif command == "/services":
            self.show_services = not self.show_services
            print(f"🔧 Services usage display: {'ON' if self.show_services else 'OFF'}")
            return True
            
        elif command == "/stats":
            await self.show_stats()
            return True
            
        elif command == "/history":
            await self.show_history()
            return True
            
        elif command == "/clear":
            self.agent.conversation_history.clear()
            print("🗑️  Conversation history cleared.")
            return True
            
        elif command.startswith("/explain "):
            query = user_input[9:].strip()
            if query:
                await self.explain_query(query)
            else:
                print("❌ Please provide a query to explain. Example: /explain What is AI?")
            return True
            
        elif command.startswith("/add "):
            content = user_input[5:].strip()
            if content:
                await self.add_knowledge(content)
            else:
                print("❌ Please provide content to add. Example: /add The sky is blue.")
            return True
            
        elif command == "/quit":
            print("👋 Goodbye!")
            return True
        
        return False
    
    async def show_stats(self):
        """Show knowledge base statistics."""
        print("\n📊 KNOWLEDGE BASE STATISTICS")
        print("-" * 40)
        
        stats = self.agent.rag_orchestrator.get_knowledge_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Show available services
        services = self.agent.service_registry.list_services()
        print(f"\n🔧 Available Services: {len(services)}")
        for name, info in services.items():
            print(f"  • {name}: {info['description']}")
    
    async def show_history(self):
        """Show conversation history."""
        print("\n💬 CONVERSATION HISTORY")
        print("-" * 40)
        
        history = self.agent.get_conversation_history()
        if not history:
            print("No conversation history yet.")
            return
        
        for i, msg in enumerate(history[-10:], 1):  # Show last 10 messages
            role = msg["role"].title()
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            print(f"{i}. {role}: {content}")
    
    async def explain_query(self, query: str):
        """Explain how the agent would approach a query."""
        print(f"\n🔍 EXPLAINING APPROACH FOR: {query}")
        print("-" * 50)
        
        try:
            explanation = await self.agent.explain_reasoning(query)
            print(explanation)
        except Exception as e:
            print(f"❌ Error explaining query: {str(e)}")
    
    async def add_knowledge(self, content: str):
        """Add knowledge to the agent."""
        try:
            await self.agent.add_knowledge(
                content=content,
                source="user_input",
                metadata={"timestamp": "interactive_demo"}
            )
            print("✅ Knowledge added successfully!")
        except Exception as e:
            print(f"❌ Error adding knowledge: {str(e)}")
    
    async def process_user_query(self, query: str):
        """Process a user query and display results."""
        print(f"\n🔍 Processing: {query}")
        print("=" * 60)
        
        try:
            # Process the query
            print("🤖 Agent is thinking...")
            response = await self.agent.process_query(query)
            
            # Display thinking process
            if self.show_thinking and response.thinking_steps:
                print("\n🤔 THINKING PROCESS:")
                for step in response.thinking_steps:
                    print(f"\n  Step {step.step_number}: {step.thought}")
                    print(f"  💭 {step.reasoning[:200]}{'...' if len(step.reasoning) > 200 else ''}")
                    if step.action:
                        print(f"  🎬 Action: {step.action}")
                    if step.action_result:
                        print(f"  📋 Result: {step.action_result}")
            
            # Display services used
            if self.show_services and response.services_used:
                print(f"\n🔧 Services Used: {', '.join(response.services_used)}")
                if response.rag_context_used:
                    print("📚 Used knowledge base context")
            
            # Display final answer
            print(f"\n💬 ANSWER:")
            print(response.final_answer)
            
            # Display metadata
            print(f"\n📊 Processing time: {response.total_time:.2f}s")
            
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def run(self):
        """Run the interactive demo."""
        
        # Initialize
        if not await self.initialize_agent():
            return
        
        self.display_banner()
        
        # Check for API keys
        if not (os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")):
            print("\n⚠️  Warning: No API keys found. The agent will use mock responses.")
            print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables for full functionality.")
        
        print("\n🎯 Ready! Ask me anything or type /help for commands.")
        
        # Main interaction loop
        while True:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    if await self.handle_command(user_input):
                        if user_input.lower() == "/quit":
                            break
                        continue
                
                # Process query
                await self.process_user_query(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Demo ended. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")


async def main():
    """Main function."""
    demo = InteractiveDemo()
    await demo.run()


if __name__ == "__main__":
    asyncio.run(main())