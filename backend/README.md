# 🧠 Thinking Agent Backend

The backend system for the Thinking Agent - a FastAPI-based REST API that provides access to the advanced LLM agent with thinking capabilities, RAG orchestration, and service selection.

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start the Server

```bash
# Basic start
python server.py

# Development mode with auto-reload
python server.py --reload

# Custom host and port
python server.py --host 0.0.0.0 --port 8080
```

### 3. Access the API

- **API Base URL**: http://127.0.0.1:8000
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 📁 Project Structure

```
backend/
├── src/                    # Core agent implementation
│   ├── agent/             # Main thinking agent
│   │   ├── thinking_agent.py
│   │   └── __init__.py
│   ├── core/              # LLM interfaces  
│   │   ├── base_llm.py
│   │   └── __init__.py
│   ├── rag/               # RAG system
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   └── __init__.py
│   ├── services/          # Service system
│   │   ├── base_service.py
│   │   ├── service_registry.py
│   │   └── __init__.py
│   └── config/            # Configuration
│       ├── settings.py
│       └── __init__.py
├── api/                   # FastAPI application
│   ├── app.py            # Main API routes
│   ├── models.py         # Pydantic models
│   └── __init__.py
├── examples/             # Usage examples
│   ├── basic_usage.py
│   └── interactive_demo.py
├── server.py             # Server startup script
├── requirements.txt      # Dependencies
├── .env.example         # Environment template
└── README.md            # This file
```

## 🌐 API Endpoints

### Chat Endpoints

#### POST `/chat`
Send a message to the thinking agent and get a comprehensive response.

**Request Body:**
```json
{
  "message": "What is machine learning?",
  "show_thinking": true,
  "use_rag": true,
  "context": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

**Response:**
```json
{
  "answer": "Machine learning is a subset of artificial intelligence...",
  "thinking_steps": [
    {
      "step_number": 1,
      "thought": "Query Analysis and Planning",
      "reasoning": "The user is asking about machine learning...",
      "action": "analyze_query",
      "action_result": "Identified as educational question",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ],
  "services_used": ["DocumentRetrievalService"],
  "rag_context_used": true,
  "processing_time": 2.5,
  "timestamp": "2024-01-01T12:00:00Z",
  "metadata": {
    "model": "gpt-4",
    "tokens_used": 150
  }
}
```

#### POST `/explain`
Get an explanation of how the agent would approach a query without executing it.

**Request Body:**
```json
{
  "message": "How would you solve a complex math problem?"
}
```

### Knowledge Management

#### POST `/knowledge`
Add new knowledge to the agent's knowledge base.

**Request Body:**
```json
{
  "content": "Python is a high-level programming language known for its simplicity and readability.",
  "source": "user_input",
  "metadata": {
    "topic": "programming",
    "language": "python",
    "date_added": "2024-01-01"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Knowledge added successfully",
  "document_id": "doc_1234567890.123"
}
```

### System Information

#### GET `/status`
Get the current status and capabilities of the thinking agent.

**Response:**
```json
{
  "status": "ready",
  "knowledge_base_stats": {
    "total_documents": 25,
    "sources": ["manual", "api", "upload"],
    "vector_store_type": "ChromaVectorStore"
  },
  "available_services": [
    "MathSolverService",
    "WebSearchService", 
    "TextSummarizationService",
    "DocumentRetrievalService"
  ],
  "configuration": {
    "default_model": "gpt-4",
    "thinking_enabled": true,
    "rag_enabled": true,
    "max_tokens": 2000,
    "chunk_size": 1000
  }
}
```

#### GET `/services`
List all available services and their capabilities.

**Response:**
```json
{
  "services": {
    "MathSolverService": {
      "description": "Solve mathematical problems and equations",
      "type": "math_solver",
      "capabilities": {
        "parameters": {
          "type": {
            "type": "string",
            "default": "general",
            "description": "Type of mathematical problem"
          }
        },
        "supported_queries": ["arithmetic", "basic algebra", "numerical calculations"]
      }
    }
  },
  "total_count": 4
}
```

### Conversation Management

#### GET `/conversation-history`
Get the agent's conversation history.

**Response:**
```json
{
  "history": [
    {
      "role": "user",
      "content": "What is AI?"
    },
    {
      "role": "assistant", 
      "content": "AI stands for Artificial Intelligence..."
    }
  ],
  "total_exchanges": 1,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### DELETE `/conversation-history`
Clear the agent's conversation history.

**Response:**
```json
{
  "message": "Conversation history cleared successfully",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Health & Monitoring

#### GET `/health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "agent_ready": "true"
}
```

#### GET `/`
Root endpoint with basic API information.

**Response:**
```json
{
  "message": "Thinking Agent API",
  "version": "1.0.0",
  "docs": "/docs",
  "status": "running"
}
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# API Keys (at least one required)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LLM Configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4
THINKING_TEMPERATURE=0.7
RESPONSE_TEMPERATURE=0.3
MAX_TOKENS=2000

# RAG Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_STORE_PATH=./data/vector_store
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5

# Agent Settings
MAX_THINKING_ITERATIONS=5
AVAILABLE_SERVICES=web_search,document_retrieval,math_solver,text_summarization

# Logging
LOG_LEVEL=INFO
```

### Server Configuration

The server can be configured via command-line arguments:

```bash
python server.py --help

# Common options:
python server.py --host 0.0.0.0         # Bind to all interfaces
python server.py --port 8080            # Use custom port
python server.py --reload               # Enable auto-reload
python server.py --workers 4            # Multiple workers (production)
python server.py --log-level debug      # Set log level
```

## 🔧 Development

### Running Tests

```bash
# Run the basic structure test
python test_structure.py

# Run interactive examples
python examples/basic_usage.py
python examples/interactive_demo.py
```

### Adding Custom Services

Create a new service by extending the `BaseService` class:

```python
# src/services/my_service.py
from .base_service import BaseService, ServiceRequest, ServiceResponse

class MyCustomService(BaseService):
    def __init__(self):
        super().__init__(
            name="MyCustomService",
            description="My custom service description"
        )
        self.service_type = "custom"
    
    async def process(self, request: ServiceRequest) -> ServiceResponse:
        # Implement your service logic here
        result = f"Processed: {request.query}"
        
        return ServiceResponse(
            content=result,
            metadata={
                "service": self.name,
                "query": request.query
            },
            success=True
        )
    
    def get_capabilities(self):
        return {
            "parameters": {},
            "supported_queries": ["custom queries"]
        }

# Register the service in the agent
from src.agent.thinking_agent import ThinkingAgent

agent = ThinkingAgent()
agent.service_registry.register_service(MyCustomService())
```

### Custom LLM Providers

Implement a custom LLM provider:

```python
# src/core/my_llm.py
from .base_llm import BaseLLM, LLMResponse

class MyCustomLLM(BaseLLM):
    def __init__(self, **kwargs):
        super().__init__("my-model", **kwargs)
    
    async def generate(self, messages, **kwargs):
        # Implement your LLM logic here
        # This is a mock implementation
        content = "This is a response from my custom LLM"
        
        return LLMResponse(
            content=content,
            metadata={"model": self.model, "provider": "custom"}
        )
    
    async def generate_stream(self, messages, **kwargs):
        # Implement streaming if needed
        content = "This is a streamed response"
        for word in content.split():
            yield word + " "

# Use with the thinking agent
from src.agent.thinking_agent import ThinkingAgent

agent = ThinkingAgent(llm=MyCustomLLM())
```

### API Extension

Add new endpoints to the FastAPI app:

```python
# api/my_routes.py
from fastapi import APIRouter
from .models import ChatRequest

router = APIRouter()

@router.post("/my-endpoint")
async def my_custom_endpoint(request: ChatRequest):
    # Your custom endpoint logic
    return {"message": "Custom endpoint response"}

# In api/app.py, include the router:
from .my_routes import router as my_router
app.include_router(my_router, prefix="/api/v1")
```

## 🚀 Deployment

### Production Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Use a Production WSGI Server**:
   ```bash
   # Install gunicorn
   pip install gunicorn
   
   # Run with gunicorn
   gunicorn api.app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

4. **Reverse Proxy** (nginx example):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### Docker Deployment (Coming Soon)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🧪 API Usage Examples

### Python Client

```python
import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # Chat with the agent
        response = await client.post(
            "http://127.0.0.1:8000/chat",
            json={
                "message": "What is quantum computing?",
                "show_thinking": True
            }
        )
        result = response.json()
        print(f"Answer: {result['answer']}")
        
        # Add knowledge
        await client.post(
            "http://127.0.0.1:8000/knowledge",
            json={
                "content": "Quantum computing uses quantum mechanics principles.",
                "source": "science_facts"
            }
        )
        
        # Get status
        status_response = await client.get("http://127.0.0.1:8000/status")
        status = status_response.json()
        print(f"Agent status: {status['status']}")

asyncio.run(main())
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

const API_BASE = 'http://127.0.0.1:8000';

async function chatWithAgent(message) {
    try {
        const response = await axios.post(`${API_BASE}/chat`, {
            message: message,
            show_thinking: true
        });
        
        console.log('Answer:', response.data.answer);
        console.log('Processing time:', response.data.processing_time);
        
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

// Usage
chatWithAgent("Explain machine learning in simple terms");
```

### cURL Examples

```bash
# Basic chat
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is artificial intelligence?",
    "show_thinking": false
  }'

# Add knowledge with metadata
curl -X POST "http://127.0.0.1:8000/knowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The Eiffel Tower was built in 1889 for the World Exposition in Paris.",
    "source": "historical_facts",
    "metadata": {
      "topic": "architecture",
      "location": "paris",
      "year": 1889
    }
  }'

# Get agent status
curl "http://127.0.0.1:8000/status"

# List available services
curl "http://127.0.0.1:8000/services"

# Clear conversation history
curl -X DELETE "http://127.0.0.1:8000/conversation-history"
```

## 🆘 Troubleshooting

### Common Issues

**Server won't start:**
- Check Python version (3.8+ required)
- Verify dependencies: `pip install -r requirements.txt`
- Check port availability: `lsof -i :8000`

**API key errors:**
- Ensure API keys are set in `.env` file
- Check environment variable names match exactly
- Verify API keys are valid and have sufficient quota

**Import errors:**
- Check Python path includes the backend directory
- Ensure virtual environment is activated
- Verify all dependencies are installed

**Performance issues:**
- Reduce `MAX_TOKENS` setting
- Use faster embedding models
- Optimize vector store configuration
- Consider using multiple workers in production

### Debug Mode

Enable debug logging:

```bash
python server.py --log-level debug
```

Or set in environment:
```env
LOG_LEVEL=DEBUG
```

### Health Checks

Monitor the API health:

```bash
# Basic health check
curl http://127.0.0.1:8000/health

# Detailed status
curl http://127.0.0.1:8000/status
```

## 📝 API Response Formats

All API responses follow consistent formats:

### Success Response
```json
{
  "answer": "Response content",
  "metadata": {},
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Status Codes
- `200`: Success
- `400`: Bad Request (invalid input)
- `422`: Validation Error (Pydantic validation failed)
- `500`: Internal Server Error

## 🔒 Security Considerations

### Production Deployment

1. **API Keys**: Store securely, never commit to version control
2. **CORS**: Configure `allow_origins` appropriately
3. **Rate Limiting**: Implement rate limiting for production
4. **Authentication**: Add authentication middleware if needed
5. **HTTPS**: Use SSL/TLS in production
6. **Input Validation**: All inputs are validated via Pydantic models

### Example Security Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

---

For more information, see the main [README.md](../README.md) or visit the interactive API documentation at `/docs` when the server is running.