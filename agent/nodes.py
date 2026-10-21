import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from tavily import TavilyClient
from .state import ResearchState

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.5)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

TRUSTED_DOMAINS = [
    ".gov", ".edu", ".org", "reuters.com", "bbc.com",
    "nytimes.com", "nature.com", "who.int", "wired.com"
]

def decompose(state: ResearchState) -> dict:
    r = llm.invoke([
        SystemMessage(content="Break the query into 2-3 specific sub-questions. Numbered list only, nothing else."),
        HumanMessage(content=state["query"])
    ])
    questions = [q.strip() for q in r.content.strip().split("\n") if q.strip()]
    return {"sub_questions": questions}

def research(state: ResearchState) -> dict:
    all_results = []
    all_sources = list(state.get("sources") or [])

    for q in state["sub_questions"]:
        data = tavily.search(q, max_results=2)
        for item in data["results"]:
            all_results.append(f"[{item['title']}] {item['content']}")
            url = item["url"]
            domain = url.split("//")[1].split("/")[0] if "//" in url else "unknown"
            all_sources.append({"title": item["title"], "url": url, "domain": domain})

    combined = "\n\n".join(all_results)
    if state.get("search_results"):
        combined = state["search_results"] + "\n\n--- NEW SEARCH ---\n\n" + combined

    return {
        "search_results": combined,
        "sources": all_sources,
        "search_count": state["search_count"] + 1
    }

def verify_sources(state: ResearchState) -> dict:
    domain_checks = []
    for s in state["sources"]:
        d = s["domain"]
        trusted = any(t in d for t in TRUSTED_DOMAINS)
        label = "✅ Trusted" if trusted else "⚠️ Unverified"
        domain_checks.append(f"{label} — {d}")

    r = llm.invoke([
        SystemMessage(content="You are a fact-checker. Do the sources agree? Any contradictions? Rate credibility: HIGH / MEDIUM / LOW. 3-4 lines max."),
        HumanMessage(content=f"Sources:\n{state['search_results'][:2000]}")
    ])

    credibility = "\n".join(domain_checks) + "\n\nCross-reference:\n" + r.content
    return {"credibility_report": credibility}

def synthesize(state: ResearchState) -> dict:
    source_list = "\n".join(
        f"[{i+1}] {s['title']} — {s['url']}"
        for i, s in enumerate(state["sources"])
    )
    r = llm.invoke([
        SystemMessage(content="Write a concise research report (300 words max). Cite using [1], [2] etc. Add a Sources section at the end with URLs. Mention disagreements if any."),
        HumanMessage(content=f"Query: {state['query']}\n\nSources:\n{state['search_results']}\n\nSource List:\n{source_list}")
    ])
    return {"report": r.content}

def quality_check(state: ResearchState) -> dict:
    r = llm.invoke([
        SystemMessage(content="Rate this report 1-10 for accuracy and completeness. Reply with ONLY a number."),
        HumanMessage(content=f"Query: {state['query']}\n\nReport:\n{state['report']}")
    ])
    digits = "".join(c for c in r.content if c.isdigit())
    score = int(digits[:2]) if digits else 5
    return {"quality_score": min(score, 10)}

def should_continue(state: ResearchState) -> str:
    if state["quality_score"] >= 7 or state["search_count"] >= 2:
        return "done"
    return "retry"