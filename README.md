# 🧠 Thinking Agent System

An advanced LLM agent system with thinking capabilities, agentic RAG orchestration, and intelligent service selection. Now with a complete API backend for easy integration.

## ✨ Features

- **🤔 Thinking & Reasoning**: Step-by-step problem analysis and planning
- **📚 RAG Orchestration**: Intelligent retrieval from knowledge bases
- **🔧 Service Selection**: Automatic selection and orchestration of specialized services
- **💬 Natural Conversation**: Maintains conversation context and history
- **� REST API**: Complete HTTP API for easy integration
- **�🎯 Multi-Provider Support**: Works with OpenAI GPT and Anthropic Claude models
- **🔌 Extensible Architecture**: Easy to add new services and capabilities

## 🚀 Quick Start

### 1. Setup

```bash
# Clone the repository
git clone <repository-url>
cd thinking-agent

# Set up virtual environment (recommended)
python3 -m venv thinking-agent-env
source thinking-agent-env/bin/activate  # On Windows: thinking-agent-env\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Set up configuration
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

### 2. Start the API Server

```bash
# Start the server
cd backend
python server.py

# The API will be available at http://127.0.0.1:8000
# View docs at http://127.0.0.1:8000/docs
```

### 3. Use the API

#### With curl:
```bash
# Basic chat
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "What is machine learning?", "show_thinking": true}'

# Add knowledge
curl -X POST "http://127.0.0.1:8000/knowledge" \
     -H "Content-Type: application/json" \
     -d '{"content": "Python is a programming language", "source": "user"}'

# Get agent status
curl "http://127.0.0.1:8000/status"
```

#### With Python client:
```python
import asyncio
import httpx

async def chat_with_agent():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/chat",
            json={
                "message": "What is artificial intelligence?",
                "show_thinking": True
            }
        )
        result = response.json()
        print(f"Answer: {result['answer']}")
        print(f"Processing time: {result['processing_time']:.2f}s")

asyncio.run(chat_with_agent())
```

#### Interactive Demo:
```bash
# Run the interactive client demo
python client_example.py
```

## 🏗️ Architecture

```
thinking-agent/
├── backend/                 # Backend API and agent system
│   ├── src/                # Core agent implementation
│   │   ├── agent/          # Main thinking agent
│   │   ├── core/           # LLM interfaces
│   │   ├── rag/            # RAG implementation
│   │   ├── services/       # Service system
│   │   └── config/         # Configuration
│   ├── api/                # FastAPI application
│   │   ├── app.py          # Main API routes
│   │   ├── models.py       # Pydantic models
│   │   └── __init__.py
│   ├── examples/           # Usage examples
│   ├── server.py           # API server script
│   └── requirements.txt    # Dependencies
├── client_example.py       # Client demo script
└── README.md               # This file
```

## 🌐 API Endpoints

### Chat & Interaction

- **POST `/chat`** - Send a message to the thinking agent
  ```json
  {
    "message": "What is machine learning?",
    "show_thinking": true,
    "use_rag": true,
    "context": {"user_id": "123"}
  }
  ```

- **POST `/explain`** - Explain reasoning without execution
- **GET `/conversation-history`** - Get conversation history  
- **DELETE `/conversation-history`** - Clear conversation history

### Knowledge Management

- **POST `/knowledge`** - Add knowledge to the agent
  ```json
  {
    "content": "Python is a programming language...",
    "source": "user_input",
    "metadata": {"topic": "programming"}
  }
  ```

### System Information

- **GET `/status`** - Get agent status and capabilities
- **GET `/services`** - List available services
- **GET `/health`** - Health check endpoint
- **GET `/docs`** - Interactive API documentation

## 🧪 Core Components

### Thinking Agent
- Multi-step reasoning process
- Query analysis and planning
- Information gathering via RAG and services
- Response synthesis and generation

### Built-in Services
- **🧮 Math Solver**: Mathematical calculations
- **🔍 Web Search**: Information retrieval (mock)
- **📄 Text Summarization**: Text analysis and summarization
- **📚 Document Retrieval**: RAG-powered knowledge search

### RAG System
- Multiple vector store backends (ChromaDB, FAISS)
- Intelligent document chunking
- Hybrid retrieval strategies
- Query expansion and reranking

## ⚙️ Configuration

Configure the system via environment variables or `.env` file:

```env
# API Keys (at least one required)
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

## 📖 Usage Examples

### Server Commands

```bash
# Start server with default settings
python backend/server.py

# Start on different port
python backend/server.py --port 8080

# Enable auto-reload for development
python backend/server.py --reload

# Start on all interfaces
python backend/server.py --host 0.0.0.0
```

### API Integration

```python
# Example Python integration
import httpx
import asyncio

class ThinkingAgentAPI:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
    
    async def chat(self, message, show_thinking=False):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat",
                json={
                    "message": message,
                    "show_thinking": show_thinking
                }
            )
            return response.json()

# Usage
api = ThinkingAgentAPI()
result = asyncio.run(api.chat("Explain quantum computing"))
print(result['answer'])
```

### cURL Examples

```bash
# Chat with thinking process
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Solve: 2x + 3 = 11",
    "show_thinking": true
  }'

# Add knowledge
curl -X POST "http://127.0.0.1:8000/knowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The capital of France is Paris",
    "source": "geography_facts"
  }'

# Get system status
curl "http://127.0.0.1:8000/status"
```

## 🔧 Development

### Adding Custom Services

```python
from backend.src.services.base_service import BaseService, ServiceRequest, ServiceResponse

class MyCustomService(BaseService):
    def __init__(self):
        super().__init__("MyService", "My custom service")
    
    async def process(self, request: ServiceRequest) -> ServiceResponse:
        # Your logic here
        return ServiceResponse(
            content="Custom response",
            metadata={"service": self.name},
            success=True
        )

# Register the service
agent.service_registry.register_service(MyCustomService())
```

### Custom LLM Providers

```python
from backend.src.core.base_llm import BaseLLM

class MyCustomLLM(BaseLLM):
    async def generate(self, messages, **kwargs):
        # Your LLM implementation
        pass

# Use with agent
agent = ThinkingAgent(llm=MyCustomLLM())
```

## 🚀 Deployment

### Production Setup

1. **Environment Variables**: Set API keys and configuration
2. **Dependencies**: Install with `pip install -r backend/requirements.txt`
3. **Process Manager**: Use gunicorn, uwsgi, or supervisor
4. **Reverse Proxy**: Configure nginx or Apache
5. **SSL/TLS**: Enable HTTPS for production

### Docker (Coming Soon)

```bash
# Build and run with Docker
docker build -t thinking-agent .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key thinking-agent
```

## 🆘 Troubleshooting

### Common Issues

**Server won't start:**
- Check dependencies: `pip install -r backend/requirements.txt`
- Verify Python version (3.8+ required)
- Check port availability: `lsof -i :8000`

**API key errors:**
- Set environment variables: `export OPENAI_API_KEY=your_key`
- Or create `backend/.env` file with keys

**Import errors:**
- Ensure proper virtual environment activation
- Check Python path and current directory

**Performance issues:**
- Reduce `MAX_TOKENS` in configuration
- Use smaller embedding models
- Optimize vector store settings

### Getting Help

- 📚 **API Docs**: Visit `/docs` endpoint when server is running
- 🔧 **Examples**: Check `client_example.py` for usage patterns
- 🧪 **Testing**: Run backend examples to verify functionality

## 🎯 Roadmap

- [ ] Docker containerization
- [ ] Authentication and authorization
- [ ] Rate limiting and quotas  
- [ ] Websocket support for real-time chat
- [ ] Frontend web interface
- [ ] Additional LLM providers
- [ ] Advanced RAG strategies
- [ ] Performance optimizations
- [ ] Monitoring and observability

## 📝 License

This project is licensed under the MIT License.

---

**Ready to get started?** 🚀

1. Install dependencies: `pip install -r backend/requirements.txt`
2. Set your API keys in `backend/.env`
3. Start the server: `python backend/server.py`
4. Visit `http://127.0.0.1:8000/docs` for API documentation
5. Try the client demo: `python client_example.py`
