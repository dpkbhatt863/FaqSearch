import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent import build_agent, get_initial_state

st.set_page_config(page_title="Research Agent", page_icon="🔬")
st.title("🔬 Agentic Research Assistant")
st.caption("Decomposes your question, searches the web, verifies sources, and writes a cited report.")

query = st.text_input(
    "What do you want to research?",
    placeholder="e.g. What impact has the 2025 US tariff policy had on global supply chains?"
)

if st.button("Research", type="primary") and query.strip():
    with st.spinner("Agent is working... this takes ~15 seconds"):
        app = build_agent()
        result = app.invoke(get_initial_state(query))

    st.divider()

    col1, col2 = st.columns(2)
    col1.metric("Quality Score", f"{result['quality_score']}/10")
    col2.metric("Web Searches", result["search_count"])

    st.subheader("📝 Report")
    st.markdown(result["report"])

    with st.expander("🔍 Sub-questions Generated"):
        for i, q in enumerate(result["sub_questions"], 1):
            st.write(f"{i}. {q}")

    with st.expander("🛡️ Source Verification"):
        st.text(result["credibility_report"])

    with st.expander("📚 Raw Sources"):
        for s in result["sources"]:
            st.markdown(f"- [{s['title'][:60]}]({s['url']}) — `{s['domain']}`")