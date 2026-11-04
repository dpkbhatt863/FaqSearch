import re
import time
from agents import run_search, run_reader, writer_chain, critic_chain

NUM_PAGES = 2
MAX_RESEARCH_CHARS = 12000

def banner(message: str):
    print("\n" + "=" * 60)
    print(message)
    print("=" * 60)


def run_research_pipeline(topic: str, num_pages: int = NUM_PAGES) -> dict:
    topic = topic.strip()
    if not topic:
        raise ValueError("Topic cannot be empty.")

    state = {}

    banner("Step 1 - Searching the web...")
    state["search"] = run_search(topic)
    print(state["search"])

    banner("Step 2 - Reading top pages...")
    urls = re.findall(r"URL: (https?://\S+)", state["search"])[:num_pages]
    summaries = []
    for u in urls:
        print(f"Reading {u}")
        try:
            summaries.append(f"[{u}]\n{run_reader(u)}")
        except Exception as e:
            summaries.append(f"[{u}]\nCould not read: {e}")
    state["reader"] = "\n\n".join(summaries) or "No pages could be read."
    print(state["reader"])

    banner("Step 3 - Writing the report...")
    research = (
        f"SEARCH RESULTS:\n{state['search']}\n\n"
        f"DETAILED PAGE SUMMARIES:\n{state['reader']}"
    )
    state["writer"] = writer_chain.invoke({
        "topic": topic,
        "research": research[:MAX_RESEARCH_CHARS],
    })
    print(state["writer"])

    banner("Step 4 - Reviewing the report...")
    state["critic"] = critic_chain.invoke({"report": state["writer"]})
    print(state["critic"])

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")

    try:
        result = run_research_pipeline(topic)
    except Exception as e:
        print(f"\nPipeline failed: {e}")
        raise SystemExit(1)

    filename = f"research_report_{int(time.time())}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(result["writer"])
        f.write("\n\n---\n\n## Critic Feedback\n\n")
        f.write(result["critic"])

    print(f"\nReport saved to {filename}")