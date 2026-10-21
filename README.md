# 🔍 FaqSearch

An AI research agent that breaks down your question, searches the web in real time, verifies source credibility, and generates a cited report, with a self-correction loop that retries when quality is low.

**[Live Demo →](https://your-app.streamlit.app)**

---

## ⚙️ How It Works

```text
User Question
     │
     ▼
[Decompose]  ── Break into 2-3 sub-questions
     │
     ▼
[Research]   ── Live web search via Tavily API
     │
     ▼
[Verify]     ── Check domain trust + cross-reference sources
     │
     ▼
[Synthesize] ── Write cited report with [1], [2] references
     │
     ▼
[Quality Check] ── Score 1-10
     │
     ├── ≥ 7 → Done ✅
     └── < 7 → Back to Research 🔄 (max 2 retries)
```

---

## ✨ Features

- **Query decomposition**: complex questions are split into searchable sub-questions
- **Live web search**: real-time results, not stale training data
- **Source verification**: domain trust-list (.gov, .edu, Reuters) plus LLM cross-referencing
- **Self-correction loop**: re-searches automatically if report quality is below 7/10
- **Cited reports**: every claim is linked back to its source URLs
- **One-click demo**: 5 sample questions built into the UI

---

## 🛠️ Tech Stack

| Layer           | Tool                | Cost                  |
|-----------------|---------------------|-----------------------|
| LLM             | Groq (Llama 3.1 8B) | Free                  |
| Web Search      | Tavily API          | Free (1000 calls/mo)  |
| Agent Framework | LangGraph           | Free                  |
| UI              | Streamlit           | Free                  |
| Hosting         | Streamlit Cloud     | Free                  |

---

## 🚀 Run Locally

**1. Clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/faqSearch.git
cd faqSearch
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Set up environment variables** (see below)

**4. Start the app**

```bash
streamlit run app.py
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_key
TAVILY_API_KEY=tvly_your_key
```

| Variable         | Where to get it                              |
|------------------|----------------------------------------------|
| `GROQ_API_KEY`   | [console.groq.com](https://console.groq.com) |
| `TAVILY_API_KEY` | [tavily.com](https://tavily.com)             |

> ⚠️ Never commit your `.env` file. Add it to `.gitignore`.

---
