"""Research agent using LangGraph.

This example shows how to run the research workflow built with LangGraph.
"""

from src.research.graph import run_research

if __name__ == "__main__":
    import asyncio

    user_query = input("Enter research request: ")
    report = asyncio.run(run_research(user_query))
    print("\n=== RESEARCH REPORT ===")
    print(report)
