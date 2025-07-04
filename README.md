# 🧠 Thinking Agent

An advanced LLM agent system with thinking capabilities, agentic RAG orchestration, and intelligent service selection.

## ✨ Features

- **🤔 Thinking & Reasoning**: Step-by-step problem analysis and planning
- **📚 RAG Orchestration**: Intelligent retrieval from knowledge bases
- **🔧 Service Selection**: Automatic selection and orchestration of specialized services
- **💬 Natural Conversation**: Maintains conversation context and history
- **🎯 Multi-Provider Support**: Works with OpenAI GPT and Anthropic Claude models
- **🔌 Extensible Architecture**: Easy to add new services and capabilities

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd thinking-agent
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up configuration:**
```bash
# Create configuration file
python main.py --setup

# Copy and edit with your API keys
cp .env.example .env
# Edit .env with your OPENAI_API_KEY or ANTHROPIC_API_KEY
```

4. **Run the agent:**
```bash
# Interactive demo
python main.py

# Single query
python main.py --query "What is machine learning?"

# Basic example
python main.py --example
```

### Quick Example

```python
import asyncio
from src.agent.thinking_agent import ThinkingAgent

async def example():
    # Create agent
    agent = ThinkingAgent()
    
    # Add knowledge
    await agent.add_knowledge(
        "Python is a programming language known for simplicity and readability.",
        source="programming_facts"
    )
    
    # Process query
    response = await agent.process_query("What do you know about Python?")
    
    print("Answer:", response.final_answer)
    print("Services used:", response.services_used)
    print("Thinking steps:", len(response.thinking_steps))

asyncio.run(example())
```

## 🏗️ Architecture

The system consists of several key components:

### Core Components

- **`ThinkingAgent`**: Main orchestrator with multi-step reasoning
- **`BaseLLM`**: Abstract interface for different LLM providers
- **`RAGOrchestrator`**: Manages document retrieval and knowledge bases
- **`ServiceRegistry`**: Handles service discovery and routing

### Built-in Services

- **🧮 Math Solver**: Evaluates mathematical expressions
- **🔍 Web Search**: Searches for information (mock implementation)
- **📄 Text Summarization**: Summarizes and analyzes text content
- **📚 Document Retrieval**: Queries the RAG knowledge base

### Thinking Process

1. **Query Analysis**: Understanding the user's request
2. **Information Gathering**: RAG retrieval + service calls
3. **Synthesis**: Reasoning about collected information
4. **Response Generation**: Creating the final answer

## 📖 Usage Examples

### Interactive Demo

```bash
python main.py
```

Commands in interactive mode:
- `/help` - Show help
- `/thinking` - Toggle thinking process display
- `/add <content>` - Add knowledge
- `/explain <query>` - Explain reasoning without executing
- `/stats` - Show knowledge base statistics

### Programmatic Usage

```python
from src.agent.thinking_agent import ThinkingAgent

# Initialize agent
agent = ThinkingAgent()

# Add knowledge
await agent.add_knowledge("Your knowledge here", source="manual")

# Process queries
response = await agent.process_query("Your question")

# Access thinking steps
for step in response.thinking_steps:
    print(f"Step {step.step_number}: {step.thought}")
    print(f"Reasoning: {step.reasoning}")
```

### Custom Services

```python
from src.services.base_service import BaseService, ServiceRequest, ServiceResponse

class CustomService(BaseService):
    def __init__(self):
        super().__init__("CustomService", "My custom service")
    
    async def process(self, request: ServiceRequest) -> ServiceResponse:
        # Your custom logic here
        return ServiceResponse(
            content="Custom response",
            metadata={"service": self.name},
            success=True
        )

# Register with agent
agent.service_registry.register_service(CustomService())
```

## ⚙️ Configuration

Configuration is handled through environment variables or a `.env` file:

```env
# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Model Settings
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4
THINKING_TEMPERATURE=0.7
RESPONSE_TEMPERATURE=0.3

# RAG Settings
VECTOR_STORE_PATH=./data/vector_store
CHUNK_SIZE=1000
TOP_K_RETRIEVAL=5
```

## 🧪 Testing

Run the test suite:

```bash
# Basic functionality test
python examples/basic_usage.py

# Interactive testing
python examples/interactive_demo.py

# Check dependencies
python main.py --check-deps
```

## 📁 Project Structure

```
thinking-agent/
├── src/
│   ├── agent/              # Main agent implementation
│   │   ├── thinking_agent.py
│   │   └── __init__.py
│   ├── core/               # Core LLM interfaces
│   │   ├── base_llm.py
│   │   └── __init__.py
│   ├── rag/                # RAG implementation
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   └── __init__.py
│   ├── services/           # Service system
│   │   ├── base_service.py
│   │   ├── service_registry.py
│   │   └── __init__.py
│   └── config/             # Configuration
│       ├── settings.py
│       └── __init__.py
├── examples/               # Usage examples
│   ├── basic_usage.py
│   └── interactive_demo.py
├── data/                   # Data storage (created automatically)
├── main.py                 # Main entry point
├── requirements.txt        # Dependencies
└── README.md
```

## 🔧 Advanced Usage

### Custom LLM Providers

```python
from src.core.base_llm import BaseLLM

class CustomLLM(BaseLLM):
    async def generate(self, messages, **kwargs):
        # Your custom LLM implementation
        pass

# Use with agent
agent = ThinkingAgent(llm=CustomLLM())
```

### Vector Store Options

The system supports multiple vector stores:

```python
from src.rag.vector_store import create_vector_store

# ChromaDB (default)
chroma_store = create_vector_store("chroma", persist_directory="./data/chroma")

# FAISS
faiss_store = create_vector_store("faiss", persist_path="./data/faiss")
```

### Service Orchestration

```python
# Get service recommendations
recommendations = agent.service_registry.get_service_recommendations(query)

# Execute multiple services
results = await agent.service_registry.execute_multiple_services(
    request, ["MathSolverService", "WebSearchService"]
)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**No API keys found:**
- Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` environment variables
- Or create a `.env` file with your keys

**Import errors:**
- Install dependencies: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

**Vector store errors:**
- ChromaDB issues: `pip install --upgrade chromadb`
- FAISS issues: `pip install faiss-cpu`

**Performance issues:**
- Reduce `MAX_TOKENS` in configuration
- Use smaller embedding models
- Limit `TOP_K_RETRIEVAL` for RAG

### Getting Help

- Check the examples in the `examples/` directory
- Run `python main.py --help` for command-line options
- Use the interactive demo to test functionality

## 🎯 Roadmap

- [ ] Additional LLM providers (Hugging Face, local models)
- [ ] More specialized services (code analysis, data processing)
- [ ] Web interface for easier interaction
- [ ] Advanced RAG strategies (hybrid search, reranking)
- [ ] Integration with external APIs and tools
- [ ] Performance optimizations and caching
