from typing import TypedDict

class ResearchState(TypedDict):
    query: str
    sub_questions: list
    search_results: str
    sources: list
    credibility_report: str
    report: str
    quality_score: int
    search_count: int

def get_initial_state(query: str) -> ResearchState:
    return {
        "query": query,
        "sub_questions": [],
        "search_results": "",
        "sources": [],
        "credibility_report": "",
        "report": "",
        "quality_score": 0,
        "search_count": 0,
    }