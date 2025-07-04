from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging

# Add app src to Python path
app_path = Path(__file__).parent.parent
sys.path.insert(0, str(app_path))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .models import (
    ChatRequest, 
    ChatResponse, 
    ThinkingStepResponse,
    KnowledgeAddRequest, 
    KnowledgeAddResponse,
    AgentStatusResponse,
    ServiceListResponse,
    ErrorResponse
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent instance
agent_instance = None

app = FastAPI(
    title="Thinking Agent API",
    description="Advanced LLM agent with thinking capabilities, RAG orchestration, and service selection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_agent():
    """Get or initialize the thinking agent."""
    global agent_instance
    
    if agent_instance is None:
        try:
            from src.agent.thinking_agent import ThinkingAgent
            
            logger.info("Initializing Thinking Agent...")
            agent_instance = ThinkingAgent()
            
            # Add some default knowledge
            await agent_instance.add_knowledge(
                """
                The Thinking Agent is an advanced AI system that combines:
                1. Multi-step thinking and reasoning capabilities
                2. RAG (Retrieval Augmented Generation) for knowledge access
                3. Intelligent service selection and orchestration
                4. Natural conversation with context awareness
                
                It can help with various tasks including answering questions,
                solving problems, analyzing text, and performing calculations.
                """,
                source="system_initialization",
                metadata={"type": "system_info"}
            )
            
            logger.info("Thinking Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Thinking Agent: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to initialize agent: {str(e)}"
            )
    
    return agent_instance


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup."""
    try:
        await get_agent()
        logger.info("API server started successfully")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Thinking Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint."""
    try:
        agent = await get_agent()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "agent_ready": "true"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - send a message to the thinking agent.
    
    This endpoint processes user input through the thinking agent's
    complete pipeline including analysis, information gathering,
    reasoning, and response generation.
    """
    try:
        agent = await get_agent()
        
        logger.info(f"Processing chat request: {request.message[:100]}...")
        
        # Process the query through the thinking agent
        response = await agent.process_query(
            query=request.message,
            context=request.context
        )
        
        # Convert thinking steps to response format
        thinking_steps = None
        if request.show_thinking and response.thinking_steps:
            thinking_steps = [
                ThinkingStepResponse(
                    step_number=step.step_number,
                    thought=step.thought,
                    reasoning=step.reasoning,
                    action=step.action,
                    action_result=step.action_result,
                    timestamp=step.timestamp
                )
                for step in response.thinking_steps
            ]
        
        return ChatResponse(
            answer=response.final_answer,
            thinking_steps=thinking_steps,
            services_used=response.services_used,
            rag_context_used=response.rag_context_used,
            processing_time=response.total_time,
            timestamp=datetime.now().isoformat(),
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )


@app.post("/knowledge", response_model=KnowledgeAddResponse)
async def add_knowledge(request: KnowledgeAddRequest):
    """
    Add knowledge to the agent's knowledge base.
    
    This endpoint allows adding new information that the agent
    can use for future queries through its RAG system.
    """
    try:
        agent = await get_agent()
        
        logger.info(f"Adding knowledge from source: {request.source}")
        
        await agent.add_knowledge(
            content=request.content,
            source=request.source,
            metadata=request.metadata
        )
        
        return KnowledgeAddResponse(
            success=True,
            message="Knowledge added successfully",
            document_id=f"doc_{datetime.now().timestamp()}"
        )
        
    except Exception as e:
        logger.error(f"Failed to add knowledge: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add knowledge: {str(e)}"
        )


@app.get("/status", response_model=AgentStatusResponse)
async def get_status():
    """
    Get the current status of the thinking agent.
    
    Returns information about the agent's state, knowledge base,
    available services, and configuration.
    """
    try:
        agent = await get_agent()
        
        # Get knowledge base stats
        kb_stats = agent.rag_orchestrator.get_knowledge_stats()
        
        # Get available services
        services = agent.service_registry.list_services()
        service_names = list(services.keys())
        
        # Get configuration info
        from src.config.settings import settings
        config_info = {
            "default_model": settings.default_model,
            "default_provider": settings.default_llm_provider,
            "thinking_enabled": True,
            "rag_enabled": True,
            "max_tokens": settings.max_tokens,
            "chunk_size": settings.chunk_size
        }
        
        return AgentStatusResponse(
            status="ready",
            knowledge_base_stats=kb_stats,
            available_services=service_names,
            configuration=config_info
        )
        
    except Exception as e:
        logger.error(f"Failed to get status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent status: {str(e)}"
        )


@app.get("/services", response_model=ServiceListResponse)
async def list_services():
    """
    List all available services and their capabilities.
    
    Returns detailed information about each service including
    descriptions, types, and supported parameters.
    """
    try:
        agent = await get_agent()
        
        services = agent.service_registry.list_services()
        
        return ServiceListResponse(
            services=services,
            total_count=len(services)
        )
        
    except Exception as e:
        logger.error(f"Failed to list services: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list services: {str(e)}"
        )


@app.post("/explain")
async def explain_reasoning(request: ChatRequest):
    """
    Explain how the agent would approach a query without executing it.
    
    This endpoint provides insight into the agent's reasoning process
    and planned approach for a given query.
    """
    try:
        agent = await get_agent()
        
        explanation = await agent.explain_reasoning(request.message)
        
        return {
            "query": request.message,
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to explain reasoning: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to explain reasoning: {str(e)}"
        )


@app.get("/conversation-history")
async def get_conversation_history():
    """
    Get the agent's conversation history.
    
    Returns the recent conversation exchanges between users and the agent.
    """
    try:
        agent = await get_agent()
        
        history = agent.get_conversation_history()
        
        return {
            "history": history,
            "total_exchanges": len(history) // 2,  # Assuming user+assistant pairs
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get conversation history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get conversation history: {str(e)}"
        )


@app.delete("/conversation-history")
async def clear_conversation_history():
    """
    Clear the agent's conversation history.
    
    Resets the conversation context for a fresh start.
    """
    try:
        agent = await get_agent()
        
        agent.conversation_history.clear()
        
        return {
            "message": "Conversation history cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to clear conversation history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear conversation history: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            error_code="INTERNAL_ERROR",
            timestamp=datetime.now().isoformat()
        ).dict()
    )