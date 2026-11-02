# 🔬 FaqSearch

An AI research pipeline that takes any question, searches the web, reads the top sources, writes a structured report, and then reviews its own work with a critic step. It comes with a Streamlit UI.

Built with **LangChain**, **Groq (gpt-oss-120b)**, **Tavily** and **Streamlit**.

<img width="1900" height="876" alt="faqSearch (1)" src="https://github.com/user-attachments/assets/3a32fe21-3d11-4c18-8d75-b28b62908493" />

## How it works

```
Topic ──> Search ──> Reader ──> Writer ──> Critic ──> Report
```

| Stage | What it does |
|---|---|
| **1. Search** | An LLM rewrites your question into 3 specific search queries. Tavily runs them, and the results are merged and de-duplicated by URL. |
| **2. Reader** | Scrapes the top pages and summarizes each one with the LLM. |
| **3. Writer** | Writes a structured report (Introduction, Key Findings, Conclusion, Sources) from the gathered research. |
| **4. Critic** | Scores the report out of 10 and lists strengths and areas to improve. |

## Tech stack

Python · LangChain · Groq · Tavily · BeautifulSoup · Streamlit

## Features

- Four-stage pipeline with live progress cards in the UI
- Query rewriting, so vague questions still produce good search queries
- Dictionary and junk domains are excluded from search results
- Graceful error handling: if a step fails, the earlier results stay visible
- Raw search results and page summaries are viewable for transparency
- Download the final report as Markdown
- Clickable example questions
- Command-line mode that saves the report and critic feedback to a `.md` file

## Project structure

```
.
├── app.py          # Streamlit UI
├── agents.py       # LLM setup, search/reader functions, writer and critic chains
├── tools.py        # Tavily search and web scraping tools
├── requirements.txt
└── .env            # API keys (not committed)

```

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/researchmind.git
cd researchmind
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add your API keys

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

- Groq key: https://console.groq.com
- Tavily key: https://tavily.com

### 4. Run it

**Web app**

```bash
streamlit run app.py
```

**Command line**

```bash
python pipeline.py
```

The CLI prints each step and saves the report plus critic feedback as `research_report_<timestamp>.md`.
