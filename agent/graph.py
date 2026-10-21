from langgraph.graph import StateGraph, START, END
from .state import ResearchState
from .nodes import decompose, research, verify_sources, synthesize, quality_check, should_continue

def build_agent():
    graph = StateGraph(ResearchState)

    graph.add_node("decompose", decompose)
    graph.add_node("research", research)
    graph.add_node("verify_sources", verify_sources)
    graph.add_node("synthesize", synthesize)
    graph.add_node("quality_check", quality_check)

    graph.add_edge(START, "decompose")
    graph.add_edge("decompose", "research")
    graph.add_edge("research", "verify_sources")
    graph.add_edge("verify_sources", "synthesize")
    graph.add_edge("synthesize", "quality_check")

    graph.add_conditional_edges(
        "quality_check",
        should_continue,
        {"retry": "research", "done": END}
    )

    return graph.compile()