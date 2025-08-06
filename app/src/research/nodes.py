"""LangGraph nodes for the research workflow."""

from __future__ import annotations

from typing import Dict

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .state import ResearchState

# Reusable LLM instance
llm = ChatOpenAI(temperature=0)

async def create_topics(state: ResearchState) -> ResearchState:
    """Generate a list of research topics from the query."""
    prompt = (
        "You are a research assistant. Based on the user question below, "
        "provide a short list of distinct topics to explore. Return the list "
        "as comma separated values.\n\nUser question: " + state["query"]
    )
    response = await llm.agenerate([[HumanMessage(content=prompt)]])
    topics = [t.strip() for t in response.generations[0][0].text.split(",")]
    state["topics"] = topics
    return state

async def build_personas(state: ResearchState) -> ResearchState:
    """Create expert personas for each topic."""
    personas = {}
    for topic in state["topics"]:
        expert_prompt = (
            f"You are a renowned expert on {topic}. Provide concise "
            f"background information about this field."
        )
        expert_resp = await llm.agenerate([[SystemMessage(content=expert_prompt)]])
        personas[topic] = expert_resp.generations[0][0].text
    state["interviews"] = personas
    return state

async def interview_expert(topic: str, intro: str) -> Dict[str, str]:
    """Conduct a short interview with an expert."""
    interviewer_prompt = (
        f"You are an interviewer speaking with an expert on {topic}.\n"
        f"Expert intro: {intro}\n"
        "Ask one insightful question about recent advances and give a short "
        "answer as the expert."
    )
    resp = await llm.agenerate([[HumanMessage(content=interviewer_prompt)]])
    return {topic: resp.generations[0][0].text}

async def writer_node(state: ResearchState) -> ResearchState:
    """Combine interview results into a full report."""
    report_parts = []
    for topic, conversation in state["interviews"].items():
        report_parts.append(f"### {topic}\n{conversation}\n")
    state["report"] = "\n".join(report_parts)
    return state
