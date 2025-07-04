from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio


class ServiceType(Enum):
    """Types of services available to the agent."""
    WEB_SEARCH = "web_search"
    DOCUMENT_RETRIEVAL = "document_retrieval"
    CODE_ANALYSIS = "code_analysis"
    DATA_ANALYSIS = "data_analysis"
    MATH_SOLVER = "math_solver"
    TEXT_SUMMARIZATION = "text_summarization"


@dataclass
class ServiceRequest:
    """Request to a service."""
    query: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


@dataclass
class ServiceResponse:
    """Response from a service."""
    content: str
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None


class BaseService(ABC):
    """Abstract base class for agent services."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.service_type = None
    
    @abstractmethod
    async def process(self, request: ServiceRequest) -> ServiceResponse:
        """Process a service request."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and parameters."""
        pass
    
    def validate_request(self, request: ServiceRequest) -> bool:
        """Validate if the request can be handled by this service."""
        return True


class WebSearchService(BaseService):
    """Web search service implementation."""
    
    def __init__(self):
        super().__init__(
            name="WebSearchService",
            description="Search the web for real-time information"
        )
        self.service_type = ServiceType.WEB_SEARCH
    
    async def process(self, request: ServiceRequest) -> ServiceResponse:
        """Process web search request."""
        try:
            # Mock implementation - replace with actual web search API
            query = request.query
            max_results = request.parameters.get("max_results", 5)
            
            # Simulate web search results
            mock_results = [
                {
                    "title": f"Result {i+1} for '{query}'",
                    "url": f"https://example.com/result{i+1}",
                    "snippet": f"This is a relevant snippet about {query} from result {i+1}."
                }
                for i in range(max_results)
            ]
            
            content = "\n".join([
                f"**{result['title']}**\n{result['snippet']}\nSource: {result['url']}\n"
                for result in mock_results
            ])
            
            return ServiceResponse(
                content=content,
                metadata={
                    "service": self.name,
                    "query": query,
                    "results_count": len(mock_results),
                    "search_type": "web"
                },
                success=True
            )
            
        except Exception as e:
            return ServiceResponse(
                content="",
                metadata={"service": self.name, "error": str(e)},
                success=False,
                error_message=f"Web search failed: {str(e)}"
            )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get web search capabilities."""
        return {
            "parameters": {
                "max_results": {
                    "type": "integer",
                    "default": 5,
                    "description": "Maximum number of search results"
                },
                "language": {
                    "type": "string", 
                    "default": "en",
                    "description": "Search language"
                }
            },
            "supported_queries": ["general information", "current events", "factual questions"]
        }


class DocumentRetrievalService(BaseService):
    """Document retrieval service using RAG."""
    
    def __init__(self, rag_orchestrator=None):
        super().__init__(
            name="DocumentRetrievalService",
            description="Retrieve relevant documents from knowledge base"
        )
        self.service_type = ServiceType.DOCUMENT_RETRIEVAL
        self.rag_orchestrator = rag_orchestrator
    
    async def process(self, request: ServiceRequest) -> ServiceResponse:
        """Process document retrieval request."""
        try:
            if not self.rag_orchestrator:
                return ServiceResponse(
                    content="",
                    metadata={"service": self.name},
                    success=False,
                    error_message="RAG orchestrator not configured"
                )
            
            query = request.query
            max_docs = request.parameters.get("max_docs", 5)
            use_hybrid = request.parameters.get("use_hybrid", True)
            
            result = await self.rag_orchestrator.query_knowledge(
                query=query,
                use_hybrid=use_hybrid,
                k=max_docs
            )
            
            content = await self.rag_orchestrator.get_context_for_query(query)
            
            return ServiceResponse(
                content=content,
                metadata={
                    "service": self.name,
                    "query": query,
                    "documents_found": result.total_found,
                    "retrieval_time": result.retrieval_time
                },
                success=True
            )
            
        except Exception as e:
            return ServiceResponse(
                content="",
                metadata={"service": self.name, "error": str(e)},
                success=False,
                error_message=f"Document retrieval failed: {str(e)}"
            )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get document retrieval capabilities."""
        return {
            "parameters": {
                "max_docs": {
                    "type": "integer",
                    "default": 5,
                    "description": "Maximum number of documents to retrieve"
                },
                "use_hybrid": {
                    "type": "boolean",
                    "default": True,
                    "description": "Use hybrid retrieval strategy"
                }
            },
            "supported_queries": ["knowledge base questions", "document content", "specific information"]
        }


class MathSolverService(BaseService):
    """Mathematical problem solving service."""
    
    def __init__(self):
        super().__init__(
            name="MathSolverService", 
            description="Solve mathematical problems and equations"
        )
        self.service_type = ServiceType.MATH_SOLVER
    
    async def process(self, request: ServiceRequest) -> ServiceResponse:
        """Process math solving request."""
        try:
            query = request.query
            problem_type = request.parameters.get("type", "general")
            
            # Simple math evaluation for basic expressions
            import re
            
            # Extract mathematical expressions
            math_expressions = re.findall(r'[\d+\-*/().\s]+', query)
            
            results = []
            for expr in math_expressions:
                expr = expr.strip()
                if expr and self._is_safe_expression(expr):
                    try:
                        result = eval(expr)
                        results.append(f"{expr} = {result}")
                    except:
                        continue
            
            if results:
                content = "Mathematical calculations:\n" + "\n".join(results)
            else:
                content = f"I can help with mathematical problems. The query '{query}' doesn't contain simple arithmetic expressions I can evaluate directly."
            
            return ServiceResponse(
                content=content,
                metadata={
                    "service": self.name,
                    "query": query,
                    "problem_type": problem_type,
                    "expressions_found": len(results)
                },
                success=True
            )
            
        except Exception as e:
            return ServiceResponse(
                content="",
                metadata={"service": self.name, "error": str(e)},
                success=False,
                error_message=f"Math solving failed: {str(e)}"
            )
    
    def _is_safe_expression(self, expr: str) -> bool:
        """Check if expression is safe to evaluate."""
        allowed_chars = set('0123456789+-*/().\s')
        return all(c in allowed_chars for c in expr)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get math solver capabilities."""
        return {
            "parameters": {
                "type": {
                    "type": "string",
                    "default": "general",
                    "description": "Type of mathematical problem"
                }
            },
            "supported_queries": ["arithmetic", "basic algebra", "numerical calculations"]
        }


class TextSummarizationService(BaseService):
    """Text summarization service."""
    
    def __init__(self):
        super().__init__(
            name="TextSummarizationService",
            description="Summarize and analyze text content"
        )
        self.service_type = ServiceType.TEXT_SUMMARIZATION
    
    async def process(self, request: ServiceRequest) -> ServiceResponse:
        """Process text summarization request."""
        try:
            text = request.query
            max_length = request.parameters.get("max_length", 200)
            summary_type = request.parameters.get("type", "extractive")
            
            # Simple extractive summarization
            sentences = text.split('.')
            
            # Take first few sentences as summary
            summary_sentences = sentences[:3]
            summary = '. '.join(sentence.strip() for sentence in summary_sentences if sentence.strip())
            
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            # Basic analysis
            word_count = len(text.split())
            sentence_count = len([s for s in sentences if s.strip()])
            
            content = f"**Summary:**\n{summary}\n\n**Analysis:**\n- Word count: {word_count}\n- Sentence count: {sentence_count}"
            
            return ServiceResponse(
                content=content,
                metadata={
                    "service": self.name,
                    "original_length": len(text),
                    "summary_length": len(summary),
                    "compression_ratio": len(summary) / len(text) if text else 0,
                    "summary_type": summary_type
                },
                success=True
            )
            
        except Exception as e:
            return ServiceResponse(
                content="",
                metadata={"service": self.name, "error": str(e)},
                success=False,
                error_message=f"Text summarization failed: {str(e)}"
            )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get text summarization capabilities."""
        return {
            "parameters": {
                "max_length": {
                    "type": "integer",
                    "default": 200,
                    "description": "Maximum length of summary"
                },
                "type": {
                    "type": "string",
                    "default": "extractive",
                    "description": "Type of summarization (extractive/abstractive)"
                }
            },
            "supported_queries": ["long text", "articles", "documents", "content analysis"]
        }