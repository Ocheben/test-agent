"""Build and run the LangGraph research workflow."""

from __future__ import annotations

from langgraph.graph import StateGraph, END
from langgraph.graph.runner import Send

from .state import ResearchState
from .nodes import create_topics, build_personas, interview_expert, writer_node


def build_graph() -> StateGraph:
    """Create and compile the research graph."""
    graph = StateGraph(ResearchState)

    graph.add_node("topics", create_topics)
    graph.add_node("personas", build_personas)

    graph.add_map(
        "interview",
        Send(interview_expert, "interviews"),
        input_key="interviews",
        output_key="interviews",
    )

    graph.add_node("writer", writer_node)

    graph.add_edge("topics", "personas")
    graph.add_edge("personas", "interview")
    graph.add_edge("interview", "writer")
    graph.add_edge("writer", END)

    return graph.compile()


def run_research(query: str) -> str:
    """Convenience function to run the full research workflow."""
    app = build_graph()
    final_state = app.invoke({"query": query})
    return final_state["report"]
