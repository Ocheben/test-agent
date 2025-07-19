"""State definition for LangGraph research workflow."""

from typing import List, Dict, TypedDict


class ResearchState(TypedDict):
    """State used across the research graph."""

    query: str
    topics: List[str]
    interviews: Dict[str, str]
    report: str
