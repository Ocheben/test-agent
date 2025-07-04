from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    context: Optional[Dict[str, Any]] = None
    show_thinking: bool = False
    use_rag: bool = True
    
    class Config:
        example = {
            "message": "What is machine learning?",
            "context": {"user_id": "123", "session_id": "abc"},
            "show_thinking": True,
            "use_rag": True
        }


class ThinkingStepResponse(BaseModel):
    """Response model for thinking steps."""
    step_number: int
    thought: str
    reasoning: str
    action: Optional[str] = None
    action_result: Optional[str] = None
    timestamp: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str
    thinking_steps: Optional[List[ThinkingStepResponse]] = None
    services_used: List[str]
    rag_context_used: bool
    processing_time: float
    timestamp: str
    metadata: Dict[str, Any]
    
    class Config:
        example = {
            "answer": "Machine learning is a subset of artificial intelligence...",
            "thinking_steps": [
                {
                    "step_number": 1,
                    "thought": "Query Analysis",
                    "reasoning": "The user is asking about machine learning...",
                    "action": "analyze_query",
                    "action_result": "Identified as educational question",
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            ],
            "services_used": ["DocumentRetrievalService"],
            "rag_context_used": True,
            "processing_time": 2.5,
            "timestamp": "2024-01-01T12:00:00Z",
            "metadata": {"model": "gpt-4", "tokens_used": 150}
        }


class KnowledgeAddRequest(BaseModel):
    """Request model for adding knowledge."""
    content: str
    source: str = "api"
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        example = {
            "content": "Python is a high-level programming language known for its simplicity.",
            "source": "user_input",
            "metadata": {"topic": "programming", "language": "python"}
        }


class KnowledgeAddResponse(BaseModel):
    """Response model for adding knowledge."""
    success: bool
    message: str
    document_id: Optional[str] = None
    
    class Config:
        example = {
            "success": True,
            "message": "Knowledge added successfully",
            "document_id": "doc_123"
        }


class AgentStatusResponse(BaseModel):
    """Response model for agent status."""
    status: str
    knowledge_base_stats: Dict[str, Any]
    available_services: List[str]
    configuration: Dict[str, Any]
    
    class Config:
        example = {
            "status": "ready",
            "knowledge_base_stats": {
                "total_documents": 25,
                "sources": ["manual", "api", "upload"]
            },
            "available_services": ["MathSolverService", "WebSearchService"],
            "configuration": {
                "default_model": "gpt-4",
                "thinking_enabled": True,
                "rag_enabled": True
            }
        }


class ServiceListResponse(BaseModel):
    """Response model for listing services."""
    services: Dict[str, Dict[str, Any]]
    total_count: int
    
    class Config:
        example = {
            "services": {
                "MathSolverService": {
                    "description": "Solve mathematical problems",
                    "type": "math_solver",
                    "capabilities": {"parameters": {}}
                }
            },
            "total_count": 3
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: str
    
    class Config:
        example = {
            "error": "Processing failed",
            "detail": "Unable to connect to LLM provider",
            "error_code": "LLM_CONNECTION_ERROR",
            "timestamp": "2024-01-01T12:00:00Z"
        }