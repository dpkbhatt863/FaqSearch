from dotenv import load_dotenv
load_dotenv()

import os
import re
from datetime import date

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is not set. Add it to your .env file.")

GEMINI_MODEL = "gemini-3.6-flash"

gemini_llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GOOGLE_API_KEY,
    max_retries=3,
)

groq_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_retries=3,
    timeout=60,
)


query_prompt = ChatPromptTemplate.from_messages([
    ("system", "You write web search queries. Output only the queries, one per line, no numbering, no quotes."),
    ("human", """Write 3 distinct, specific web search queries to research this question thoroughly.
Keep the full meaning of the question, include the current year ({year}) where relevant,
and make each query a complete phrase, never a single word.

Question: {topic}"""),
])
query_chain = query_prompt | gemini_llm | StrOutputParser()


def run_search(topic: str) -> str:
    try:
        raw = query_chain.invoke({"topic": topic, "year": date.today().year})
        queries = [q.strip(" -•\t\"") for q in raw.splitlines() if len(q.split()) >= 3][:3]
    except Exception:
        queries = []

    if not queries:
        queries = [topic]

    seen, blocks = set(), []
    for q in queries:
        result = web_search.invoke({"query": q})
        for block in result.split("\n----\n"):
            m = re.search(r"URL: (\S+)", block)
            if m and m.group(1) not in seen:
                seen.add(m.group(1))
                blocks.append(block)

    return "\n----\n".join(blocks) if blocks else "No results found."


reader_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a research reader. Summarize the extracted page content faithfully."),
    ("human", "URL: {url}\n\nPage content:\n{content}\n\nSummarize the key information."),
])
reader_chain = reader_prompt | gemini_llm | StrOutputParser()


def run_reader(url: str) -> str:
    content = scrape_url.invoke({"url": url})
    return reader_chain.invoke({"url": url, "content": content})


writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Use ONLY the research above for facts and figures. If the research does not
cover something, say so instead of using your own knowledge. Every key finding
must be backed by a URL from the research.

Be detailed, factual and professional."""),
])
writer_chain = writer_prompt | gemini_llm | StrOutputParser()


critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])
critic_chain = critic_prompt | groq_llm | StrOutputParser()