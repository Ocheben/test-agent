from typing import Dict, Any, List, Optional, Union
import asyncio
import json
from dataclasses import dataclass
from datetime import datetime

from ..core.base_llm import BaseLLM, create_llm, LLMResponse
from ..rag.retriever import RAGOrchestrator
from ..services.service_registry import ServiceRegistry
from ..services.base_service import ServiceRequest, ServiceResponse, DocumentRetrievalService
from ..config.settings import settings


@dataclass
class ThinkingStep:
    """Represents a single step in the thinking process."""
    step_number: int
    thought: str
    reasoning: str
    action: Optional[str] = None
    action_result: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class AgentResponse:
    """Complete response from the thinking agent."""
    final_answer: str
    thinking_steps: List[ThinkingStep]
    services_used: List[str]
    rag_context_used: bool
    metadata: Dict[str, Any]
    total_time: float


class ThinkingAgent:
    """
    Advanced LLM agent with thinking capabilities, RAG orchestration, and service selection.
    """
    
    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        rag_orchestrator: Optional[RAGOrchestrator] = None,
        service_registry: Optional[ServiceRegistry] = None,
        thinking_model: Optional[BaseLLM] = None
    ):
        # Initialize LLM for final responses
        self.llm = llm or create_llm(
            provider=settings.default_llm_provider,
            model=settings.default_model,
            api_key=settings.openai_api_key or settings.anthropic_api_key,
            temperature=settings.response_temperature,
            max_tokens=settings.max_tokens
        )
        
        # Initialize thinking LLM (can be different for reasoning)
        self.thinking_llm = thinking_model or create_llm(
            provider=settings.default_llm_provider,
            model=settings.default_model,
            api_key=settings.openai_api_key or settings.anthropic_api_key,
            temperature=settings.thinking_temperature,
            max_tokens=settings.max_tokens
        )
        
        # Initialize RAG and services
        self.rag_orchestrator = rag_orchestrator or RAGOrchestrator()
        self.service_registry = service_registry or ServiceRegistry()
        
        # Register RAG service with the registry
        doc_retrieval_service = DocumentRetrievalService(self.rag_orchestrator)
        self.service_registry.register_service(doc_retrieval_service)
        
        # Agent state
        self.conversation_history: List[Dict[str, str]] = []
        self.thinking_history: List[ThinkingStep] = []
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Process a user query through the complete thinking and action pipeline.
        """
        start_time = asyncio.get_event_loop().time()
        
        thinking_steps = []
        services_used = []
        rag_context_used = False
        
        # Step 1: Initial analysis and planning
        planning_step = await self._think_and_plan(query, context)
        thinking_steps.append(planning_step)
        
        # Step 2: Gather information (RAG + Services)
        information_gathering_step, gathered_info, used_services = await self._gather_information(
            query, planning_step.reasoning
        )
        thinking_steps.append(information_gathering_step)
        services_used.extend(used_services)
        
        if gathered_info:
            rag_context_used = True
        
        # Step 3: Reasoning and synthesis
        reasoning_step = await self._reason_and_synthesize(query, gathered_info, planning_step.reasoning)
        thinking_steps.append(reasoning_step)
        
        # Step 4: Generate final response
        final_response = await self._generate_final_response(
            query, thinking_steps, gathered_info, context
        )
        
        total_time = asyncio.get_event_loop().time() - start_time
        
        # Update conversation history
        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({"role": "assistant", "content": final_response})
        
        return AgentResponse(
            final_answer=final_response,
            thinking_steps=thinking_steps,
            services_used=list(set(services_used)),
            rag_context_used=rag_context_used,
            metadata={
                "query": query,
                "context": context,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.llm.model,
                "thinking_model_used": self.thinking_llm.model
            },
            total_time=total_time
        )
    
    async def _think_and_plan(self, query: str, context: Optional[Dict[str, Any]] = None) -> ThinkingStep:
        """First thinking step: analyze the query and create a plan."""
        
        thinking_prompt = f"""
You are an advanced AI agent analyzing a user query. Break down the query and create a plan.

User Query: {query}
Context: {context or 'None provided'}

Think through this step by step:
1. What is the user really asking for?
2. What type of information or services might be needed?
3. What's the best approach to answer this comprehensively?
4. Are there any potential challenges or edge cases?

Provide your analysis and reasoning:
"""
        
        messages = [
            {"role": "system", "content": "You are a thoughtful AI assistant that analyzes queries deeply."},
            {"role": "user", "content": thinking_prompt}
        ]
        
        response = await self.thinking_llm.generate(messages)
        
        return ThinkingStep(
            step_number=1,
            thought="Query Analysis and Planning",
            reasoning=response.content,
            timestamp=datetime.now().isoformat()
        )
    
    async def _gather_information(
        self, 
        query: str, 
        planning_reasoning: str
    ) -> tuple[ThinkingStep, str, List[str]]:
        """Second thinking step: gather information from RAG and services."""
        
        gathered_info = ""
        used_services = []
        
        # Determine what information sources to use
        decision_prompt = f"""
Based on this query and planning reasoning, decide what information sources to use:

Query: {query}
Planning: {planning_reasoning}

Available services: {list(self.service_registry.services.keys())}

Should I:
1. Search the knowledge base (RAG)?
2. Use external services? If so, which ones?
3. Both?

Respond with JSON format:
{{
    "use_rag": true/false,
    "services_to_use": ["service1", "service2"],
    "reasoning": "explanation"
}}
"""
        
        messages = [
            {"role": "system", "content": "You are an AI that decides information gathering strategies."},
            {"role": "user", "content": decision_prompt}
        ]
        
        decision_response = await self.thinking_llm.generate(messages)
        
        try:
            # Parse decision (with fallback)
            decision_text = decision_response.content.strip()
            if decision_text.startswith("```json"):
                decision_text = decision_text.replace("```json", "").replace("```", "").strip()
            
            decision = json.loads(decision_text)
        except:
            # Fallback to basic service selection
            decision = {
                "use_rag": True,
                "services_to_use": self.service_registry.get_service_recommendations(query)[:1],
                "reasoning": "Fallback decision due to parsing error"
            }
        
        information_parts = []
        
        # Use RAG if decided
        if decision.get("use_rag", False):
            try:
                rag_context = await self.rag_orchestrator.get_context_for_query(query)
                if rag_context.strip():
                    information_parts.append(f"Knowledge Base Information:\n{rag_context}")
            except Exception as e:
                information_parts.append(f"Knowledge base unavailable: {str(e)}")
        
        # Use external services if decided
        services_to_use = decision.get("services_to_use", [])
        for service_name in services_to_use:
            try:
                service_request = ServiceRequest(
                    query=query,
                    parameters={},
                    context={"source": "thinking_agent"}
                )
                
                service_response = await self.service_registry.route_request(
                    service_request, service_name
                )
                
                if service_response.success:
                    information_parts.append(
                        f"Service ({service_name}) Information:\n{service_response.content}"
                    )
                    used_services.append(service_name)
                
            except Exception as e:
                information_parts.append(f"Service {service_name} error: {str(e)}")
        
        gathered_info = "\n\n---\n\n".join(information_parts)
        
        return ThinkingStep(
            step_number=2,
            thought="Information Gathering",
            reasoning=f"Decision: {decision.get('reasoning', 'Used available sources')}\n\nGathered:\n{gathered_info[:500]}{'...' if len(gathered_info) > 500 else ''}",
            action=f"Used RAG: {decision.get('use_rag', False)}, Services: {services_to_use}",
            action_result=f"Retrieved {len(information_parts)} information sources",
            timestamp=datetime.now().isoformat()
        ), gathered_info, used_services
    
    async def _reason_and_synthesize(
        self, 
        query: str, 
        gathered_info: str, 
        planning_reasoning: str
    ) -> ThinkingStep:
        """Third thinking step: reason about the information and synthesize insights."""
        
        synthesis_prompt = f"""
Now analyze and synthesize the gathered information to answer the user's query:

Original Query: {query}
Planning: {planning_reasoning}

Gathered Information:
{gathered_info}

Think through:
1. What are the key insights from the gathered information?
2. How does this information address the user's query?
3. Are there any gaps, contradictions, or limitations?
4. What would be the most helpful and accurate response?

Provide your synthesis and reasoning:
"""
        
        messages = [
            {"role": "system", "content": "You are an AI that synthesizes information to create comprehensive answers."},
            {"role": "user", "content": synthesis_prompt}
        ]
        
        response = await self.thinking_llm.generate(messages)
        
        return ThinkingStep(
            step_number=3,
            thought="Information Synthesis and Reasoning",
            reasoning=response.content,
            timestamp=datetime.now().isoformat()
        )
    
    async def _generate_final_response(
        self,
        query: str,
        thinking_steps: List[ThinkingStep],
        gathered_info: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate the final response to the user."""
        
        # Build context from thinking process
        thinking_summary = "\n".join([
            f"Step {step.step_number}: {step.thought}\n{step.reasoning[:200]}{'...' if len(step.reasoning) > 200 else ''}"
            for step in thinking_steps
        ])
        
        final_prompt = f"""
Based on your thinking process and gathered information, provide a clear, helpful, and comprehensive response to the user's query.

User Query: {query}
Context: {context or 'None'}

Your Thinking Process:
{thinking_summary}

Gathered Information:
{gathered_info[:2000] if gathered_info else 'No external information gathered'}

Provide a direct, helpful answer that:
1. Directly addresses the user's question
2. Incorporates relevant insights from your research
3. Is clear and well-structured
4. Acknowledges any limitations or uncertainties

Response:
"""
        
        # Include conversation history for context
        messages = []
        if self.conversation_history:
            messages.extend(self.conversation_history[-4:])  # Last 2 exchanges
        
        messages.extend([
            {"role": "system", "content": "You are a helpful AI assistant that provides comprehensive, accurate responses based on careful analysis and research."},
            {"role": "user", "content": final_prompt}
        ])
        
        response = await self.llm.generate(messages)
        return response.content
    
    async def add_knowledge(self, content: str, source: str = "user", metadata: Optional[Dict[str, Any]] = None):
        """Add knowledge to the agent's RAG system."""
        await self.rag_orchestrator.add_knowledge(content, source, metadata)
    
    def get_thinking_history(self) -> List[ThinkingStep]:
        """Get the complete thinking history."""
        return self.thinking_history.copy()
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history.copy()
    
    async def explain_reasoning(self, query: str) -> str:
        """Explain how the agent would approach a given query without executing it."""
        
        planning_step = await self._think_and_plan(query, None)
        
        explanation = f"""
**Query Analysis:**
{planning_step.reasoning}

**Recommended Services:**
{', '.join(self.service_registry.get_service_recommendations(query))}

**Available Knowledge Base:**
{self.rag_orchestrator.get_knowledge_stats()}

**Approach:**
I would gather information from the most relevant sources, synthesize the findings, and provide a comprehensive response based on the analysis above.
"""
        return explanation