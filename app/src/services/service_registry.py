from typing import Dict, List, Optional, Any
from .base_service import BaseService, ServiceRequest, ServiceResponse, ServiceType
from .base_service import WebSearchService, DocumentRetrievalService, MathSolverService, TextSummarizationService
import asyncio


class ServiceRegistry:
    """Registry for managing agent services."""
    
    def __init__(self):
        self.services: Dict[str, BaseService] = {}
        self.service_types: Dict[ServiceType, List[BaseService]] = {}
        self._initialize_default_services()
    
    def _initialize_default_services(self):
        """Initialize default services."""
        default_services = [
            WebSearchService(),
            MathSolverService(), 
            TextSummarizationService()
        ]
        
        for service in default_services:
            self.register_service(service)
    
    def register_service(self, service: BaseService) -> None:
        """Register a new service."""
        self.services[service.name] = service
        
        if service.service_type:
            if service.service_type not in self.service_types:
                self.service_types[service.service_type] = []
            self.service_types[service.service_type].append(service)
    
    def get_service(self, name: str) -> Optional[BaseService]:
        """Get a service by name."""
        return self.services.get(name)
    
    def get_services_by_type(self, service_type: ServiceType) -> List[BaseService]:
        """Get all services of a specific type."""
        return self.service_types.get(service_type, [])
    
    def list_services(self) -> Dict[str, Dict[str, Any]]:
        """List all registered services with their capabilities."""
        return {
            name: {
                "description": service.description,
                "type": service.service_type.value if service.service_type else None,
                "capabilities": service.get_capabilities()
            }
            for name, service in self.services.items()
        }
    
    async def route_request(self, request: ServiceRequest, service_name: Optional[str] = None) -> ServiceResponse:
        """Route a request to the appropriate service."""
        
        if service_name:
            service = self.get_service(service_name)
            if service:
                return await service.process(request)
            else:
                return ServiceResponse(
                    content="",
                    metadata={"error": f"Service '{service_name}' not found"},
                    success=False,
                    error_message=f"Service '{service_name}' not found"
                )
        
        # Auto-select service based on query content
        selected_service = self._select_service_for_query(request.query)
        
        if selected_service:
            return await selected_service.process(request)
        else:
            return ServiceResponse(
                content="",
                metadata={"error": "No suitable service found"},
                success=False,
                error_message="No suitable service found for the query"
            )
    
    def _select_service_for_query(self, query: str) -> Optional[BaseService]:
        """Automatically select the best service for a query."""
        query_lower = query.lower()
        
        # Math-related keywords
        math_keywords = ['calculate', 'solve', 'equation', 'math', 'arithmetic', '+', '-', '*', '/', '=']
        if any(keyword in query_lower for keyword in math_keywords):
            math_services = self.get_services_by_type(ServiceType.MATH_SOLVER)
            if math_services:
                return math_services[0]
        
        # Web search keywords
        web_keywords = ['search', 'find', 'current', 'latest', 'news', 'recent', 'what is', 'who is']
        if any(keyword in query_lower for keyword in web_keywords):
            web_services = self.get_services_by_type(ServiceType.WEB_SEARCH)
            if web_services:
                return web_services[0]
        
        # Summarization keywords
        summary_keywords = ['summarize', 'summary', 'analyze', 'analyze text', 'key points']
        if any(keyword in query_lower for keyword in summary_keywords):
            summary_services = self.get_services_by_type(ServiceType.TEXT_SUMMARIZATION)
            if summary_services:
                return summary_services[0]
        
        # Document retrieval keywords
        doc_keywords = ['document', 'knowledge', 'information', 'retrieve', 'find in']
        if any(keyword in query_lower for keyword in doc_keywords):
            doc_services = self.get_services_by_type(ServiceType.DOCUMENT_RETRIEVAL)
            if doc_services:
                return doc_services[0]
        
        # Default to web search if available
        web_services = self.get_services_by_type(ServiceType.WEB_SEARCH)
        if web_services:
            return web_services[0]
        
        # Fallback to first available service
        if self.services:
            return list(self.services.values())[0]
        
        return None
    
    async def execute_multiple_services(
        self, 
        request: ServiceRequest, 
        service_names: List[str]
    ) -> Dict[str, ServiceResponse]:
        """Execute request on multiple services concurrently."""
        
        tasks = []
        valid_services = []
        
        for service_name in service_names:
            service = self.get_service(service_name)
            if service:
                valid_services.append(service_name)
                tasks.append(service.process(request))
        
        if not tasks:
            return {}
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = {}
        for i, (service_name, response) in enumerate(zip(valid_services, responses)):
            if isinstance(response, Exception):
                results[service_name] = ServiceResponse(
                    content="",
                    metadata={"error": str(response)},
                    success=False,
                    error_message=f"Service execution failed: {str(response)}"
                )
            else:
                results[service_name] = response
        
        return results
    
    def get_service_recommendations(self, query: str) -> List[str]:
        """Get recommended services for a query."""
        recommendations = []
        query_lower = query.lower()
        
        # Score each service based on relevance
        service_scores = []
        
        for service in self.services.values():
            score = 0
            capabilities = service.get_capabilities()
            
            # Check supported queries
            if 'supported_queries' in capabilities:
                for supported_query in capabilities['supported_queries']:
                    if any(word in query_lower for word in supported_query.lower().split()):
                        score += 1
            
            # Check service type relevance
            if service.service_type == ServiceType.MATH_SOLVER:
                math_keywords = ['calculate', 'solve', 'equation', 'math']
                if any(keyword in query_lower for keyword in math_keywords):
                    score += 2
            
            elif service.service_type == ServiceType.WEB_SEARCH:
                web_keywords = ['search', 'find', 'current', 'latest']
                if any(keyword in query_lower for keyword in web_keywords):
                    score += 2
            
            elif service.service_type == ServiceType.TEXT_SUMMARIZATION:
                summary_keywords = ['summarize', 'summary', 'analyze']
                if any(keyword in query_lower for keyword in summary_keywords):
                    score += 2
            
            service_scores.append((service.name, score))
        
        # Sort by score and return top recommendations
        service_scores.sort(key=lambda x: x[1], reverse=True)
        recommendations = [name for name, score in service_scores if score > 0]
        
        # If no good matches, return all services
        if not recommendations:
            recommendations = list(self.services.keys())
        
        return recommendations[:3]  # Return top 3 recommendations