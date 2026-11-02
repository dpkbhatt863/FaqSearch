import re
import time
import html
import streamlit as st
from agents import run_search, run_reader, writer_chain, critic_chain

NUM_PAGES = 2

EXAMPLES = [
    "Which jobs will be most paid after 5 years?",
    "How is generative AI changing legal e-discovery?",
    "What are the best ways to learn LLM engineering in 2026?",
    "What are the latest breakthroughs in fusion energy?",
]

st.set_page_config(
    page_title="FaqSearch",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #fafafa; color: #1f2328; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1100px; }

.hero { text-align: center; padding: 2.5rem 0 1.5rem; }
.hero-eyebrow {
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: #4f46e5; margin-bottom: 0.6rem;
}
.hero h1 {
    font-size: clamp(2.2rem, 5vw, 3.2rem); font-weight: 700;
    letter-spacing: -0.02em; color: #111827; margin: 0 0 0.6rem;
}
.hero h1 span { color: #4f46e5; }
.hero-sub { font-size: 1rem; color: #6b7280; max-width: 480px; margin: 0 auto; line-height: 1.6; }

.divider { height: 1px; background: #e5e7eb; margin: 1.5rem 0; }

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem;
}

.stTextInput > div > div > input {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    color: #111827 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 2px rgba(79,70,229,0.15) !important;
}
.stTextInput > label { font-size: 0.8rem !important; font-weight: 600 !important; color: #374151 !important; }

.stButton > button, .stDownloadButton > button {
    background: #4f46e5 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.6rem !important;
}
.stButton > button:hover, .stDownloadButton > button:hover { background: #4338ca !important; }
.stButton > button:disabled { background: #c7c9d1 !important; color: #ffffff !important; }

.st-key-examples .stButton > button {
    background: #ffffff !important;
    color: #374151 !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    border: 1px solid #e5e7eb !important;
    padding: 0.45rem 0.9rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
}
.st-key-examples .stButton > button:hover {
    background: #f5f5ff !important;
    border-color: #4f46e5 !important;
    color: #4f46e5 !important;
}
.st-key-examples .stButton > button:disabled {
    background: #f3f4f6 !important;
    color: #9ca3af !important;
}

.examples-label {
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #9ca3af; margin: 1rem 0 0.5rem;
}

.step-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-left: 3px solid #e5e7eb;
    border-radius: 8px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.7rem;
}
.step-card.active { border-left-color: #4f46e5; }
.step-card.done   { border-left-color: #10b981; }
.step-card.failed { border-left-color: #ef4444; }

.step-header { display: flex; align-items: center; gap: 0.7rem; }
.step-num   { font-size: 0.75rem; color: #9ca3af; font-weight: 600; }
.step-title { font-size: 0.95rem; font-weight: 600; color: #111827; }
.step-desc  { font-size: 0.8rem; color: #6b7280; margin-top: 0.25rem; }
.step-status { margin-left: auto; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.05em; }
.status-waiting { color: #9ca3af; }
.status-running { color: #4f46e5; }
.status-done    { color: #10b981; }
.status-failed  { color: #ef4444; }

.result-panel { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 1rem 1.2rem; }
.result-panel-title { font-size: 0.75rem; font-weight: 600; color: #6b7280; text-transform: uppercase; margin-bottom: 0.6rem; }
.result-content { font-size: 0.88rem; line-height: 1.7; color: #374151; white-space: pre-wrap; }

.panel-label {
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.06em;
    text-transform: uppercase; margin-bottom: 0.8rem;
}
.panel-label.orange { color: #4f46e5; }
.panel-label.green  { color: #10b981; }

.section-heading { font-size: 1.1rem; font-weight: 600; color: #111827; margin: 1.5rem 0 0.8rem; }
.notice { font-size: 0.75rem; color: #9ca3af; text-align: center; margin-top: 3rem; }
</style>
""", unsafe_allow_html=True)


STEPS = [
    ("search", "01", "Search", "Finds recent sources on the web"),
    ("reader", "02", "Reader", "Scrapes & summarizes top pages"),
    ("writer", "03", "Writer Chain", "Drafts the full research report"),
    ("critic", "04", "Critic Chain", "Reviews & scores the report"),
]

STATUS_MAP = {
    "waiting": ("WAITING", "status-waiting", ""),
    "running": ("● RUNNING", "status-running", "active"),
    "done": ("✓ DONE", "status-done", "done"),
    "failed": ("✕ FAILED", "status-failed", "failed"),
}


def step_html(num, title, state, desc):
    label, status_cls, card_cls = STATUS_MAP[state]
    return f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {status_cls}">{label}</span>
        </div>
        <div class="step-desc">{desc}</div>
    </div>
    """


def step_states(results, running, failed_step=None):
    states, found_running = {}, False
    for key, *_ in STEPS:
        if key in results:
            states[key] = "done"
        elif failed_step == key:
            states[key] = "failed"
        elif running and not found_running and failed_step is None:
            states[key] = "running"
            found_running = True
        else:
            states[key] = "waiting"
    return states


def set_topic(question):
    st.session_state.topic_input = question


st.session_state.setdefault("results", {})
st.session_state.setdefault("running", False)
st.session_state.setdefault("done", False)
st.session_state.setdefault("topic_val", "")
st.session_state.setdefault("failed_step", None)


st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">AI Research Pipeline</div>
    <h1>Faq<span>Search</span></h1>
    <p class="hero-sub">
        A four-stage pipeline: searching, scraping, writing and critiquing,
        to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    with st.container(border=True):
        topic = st.text_input(
            "Research Topic",
            placeholder="e.g. Quantum computing breakthroughs in 2026",
            key="topic_input",
        )
        run_btn = st.button(
            "Run Research Pipeline",
            use_container_width=True,
            disabled=st.session_state.running,
        )
        status_box = st.empty()

    st.markdown('<div class="examples-label">Try an example</div>', unsafe_allow_html=True)
    with st.container(key="examples"):
        for i, question in enumerate(EXAMPLES):
            st.button(
                question,
                key=f"example_{i}",
                on_click=set_topic,
                args=(question,),
                use_container_width=True,
                disabled=st.session_state.running,
            )

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)
    placeholders = {key: st.empty() for key, *_ in STEPS}


def render_pipeline(results, running, failed_step=None):
    states = step_states(results, running, failed_step)
    for key, num, title, desc in STEPS:
        placeholders[key].markdown(step_html(num, title, states[key], desc), unsafe_allow_html=True)


def show_status(step_number, message):
    status_box.info(f"Running · Step {step_number} of 4: {message}")


render_pipeline(st.session_state.results, st.session_state.running, st.session_state.failed_step)


if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.topic_val = topic.strip()
        st.session_state.results = {}
        st.session_state.failed_step = None
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()


if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_val
    current = "search"

    try:
        current = "search"
        render_pipeline(results, True)
        show_status(1, "Searching the web…")
        results["search"] = run_search(topic_val)
        st.session_state.results = dict(results)

        current = "reader"
        render_pipeline(results, True)
        show_status(2, "Reading top resources…")
        urls = re.findall(r"URL: (https?://\S+)", results["search"])[:NUM_PAGES]
        summaries = []
        for u in urls:
            try:
                summaries.append(f"[{u}]\n{run_reader(u)}")
            except Exception as e:
                summaries.append(f"[{u}]\nCould not read: {e}")
        results["reader"] = "\n\n".join(summaries) or "No pages could be read."
        st.session_state.results = dict(results)

        current = "writer"
        render_pipeline(results, True)
        show_status(3, "Drafting the report…")
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED PAGE SUMMARIES:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined[:12000],
        })
        st.session_state.results = dict(results)

        current = "critic"
        render_pipeline(results, True)
        show_status(4, "Reviewing the report…")
        results["critic"] = critic_chain.invoke({"report": results["writer"]})
        st.session_state.results = dict(results)

        status_box.empty()
        st.session_state.running = False
        st.session_state.done = True
        st.rerun()

    except Exception as e:
        st.session_state.running = False
        st.session_state.failed_step = current
        st.session_state.results = dict(results)
        render_pipeline(results, False, current)
        status_box.error(f"The {current} step failed: {e}")


r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("Search Results (raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel"><div class="result-panel-title">Search Output</div>'
                f'<div class="result-content">{html.escape(r["search"])}</div></div>',
                unsafe_allow_html=True,
            )

    if "reader" in r:
        with st.expander("Page Summaries (raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel"><div class="result-panel-title">Reader Output</div>'
                f'<div class="result-content">{html.escape(r["reader"])}</div></div>',
                unsafe_allow_html=True,
            )

    if "writer" in r:
        with st.container(border=True):
            st.markdown('<div class="panel-label orange">Final Research Report</div>', unsafe_allow_html=True)
            st.markdown(r["writer"])
        st.download_button(
            label="Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="panel-label green">Critic Feedback</div>', unsafe_allow_html=True)
            st.markdown(r["critic"])


st.markdown("""
<div class="notice">
    FaqSearch · Powered by LangChain + Groq · Built with Streamlit
</div>
""", unsafe_allow_html=True)