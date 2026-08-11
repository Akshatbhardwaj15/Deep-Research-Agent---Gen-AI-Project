"""
streamlit_app.py
-----------------
Streamlit front-end for the multi-agent research pipeline
(search agent -> reader agent -> writer chain -> critic chain).

Run with:
    streamlit run streamlit_app.py

Place this file in the same folder as agents.py, tools.py and pipeline.py.
"""

import time
import streamlit as st

from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain


# ----------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="AI Research Pipeline",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# Minimal styling
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main .block-container {padding-top: 2rem; max-width: 1100px;}
    .stChatMessage, .report-box {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        background: rgba(128,128,128,0.04);
    }
    h1 {font-weight: 700;}
    .score-badge {
        display: inline-block;
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        background: linear-gradient(90deg,#6366f1,#8b5cf6);
        color: white;
        font-weight: 600;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------
defaults = {
    "search_results": None,
    "scraped_content": None,
    "report": None,
    "feedback": None,
    "running": False,
    "history": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🔎 Research Pipeline")
    st.caption("Search → Read → Write → Critique, powered by LangChain agents.")

    st.markdown("---")
    st.markdown("### Pipeline stages")
    st.markdown(
        "1. **Search Agent** — finds recent, relevant sources\n"
        "2. **Reader Agent** — scrapes the best source for depth\n"
        "3. **Writer Chain** — drafts a structured report\n"
        "4. **Critic Chain** — scores and reviews the report"
    )

    st.markdown("---")
    if st.session_state["history"]:
        st.markdown("### Past topics")
        for t in reversed(st.session_state["history"][-8:]):
            st.markdown(f"- {t}")

    st.markdown("---")
    if st.button("🗑️ Clear results", use_container_width=True):
        for k in ["search_results", "scraped_content", "report", "feedback"]:
            st.session_state[k] = None
        st.rerun()


# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.title("🔎 AI Research Pipeline")
st.caption(
    "Enter a topic and let a chain of agents search the web, read the best "
    "source, draft a report, and critique it — all in one pass."
)

with st.form("topic_form"):
    col1, col2 = st.columns([5, 1])
    with col1:
        topic = st.text_input(
            "Research topic",
            placeholder="e.g. The impact of AI agents on software engineering jobs",
            label_visibility="collapsed",
        )
    with col2:
        submitted = st.form_submit_button(
            "Run 🚀", use_container_width=True, disabled=st.session_state["running"]
        )


# ----------------------------------------------------------------------
# Helper: run a single pipeline stage inside a status block
# ----------------------------------------------------------------------
def run_pipeline(topic: str):
    st.session_state["running"] = True
    st.session_state["history"].append(topic)

    # ---- Stage 1: search agent -----------------------------------
    with st.status("🔍 Searching the web for sources...", expanded=True) as status:
        t0 = time.time()
        search_agent = build_search_agent()
        result = search_agent.invoke(
            {"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]}
        )
        search_results = result["messages"][-1].content
        st.session_state["search_results"] = search_results
        status.update(
            label=f"✅ Search complete ({time.time() - t0:.1f}s)",
            state="complete",
            expanded=False,
        )

    # ---- Stage 2: reader agent -------------------------------------
    with st.status("📖 Reading the most relevant source...", expanded=True) as status:
        t0 = time.time()
        reader_agent = build_reader_agent()
        result = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Based on the following search results about '{topic}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{search_results[:800]}",
                    )
                ]
            }
        )
        scraped_content = result["messages"][-1].content
        st.session_state["scraped_content"] = scraped_content
        status.update(
            label=f"✅ Reading complete ({time.time() - t0:.1f}s)",
            state="complete",
            expanded=False,
        )

    # ---- Stage 3: writer chain --------------------------------------
    with st.status("✍️ Writing the report...", expanded=True) as status:
        t0 = time.time()
        research_combined = (
            f"SEARCH RESULTS:\n{search_results}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{scraped_content}"
        )
        report = writer_chain.invoke({"topic": topic, "research": research_combined})
        st.session_state["report"] = report
        status.update(
            label=f"✅ Report drafted ({time.time() - t0:.1f}s)",
            state="complete",
            expanded=False,
        )

    # ---- Stage 4: critic chain ---------------------------------------
    with st.status("🧐 Critiquing the report...", expanded=True) as status:
        t0 = time.time()
        feedback = critic_chain.invoke({"report": report})
        st.session_state["feedback"] = feedback
        status.update(
            label=f"✅ Critique complete ({time.time() - t0:.1f}s)",
            state="complete",
            expanded=False,
        )

    st.session_state["running"] = False


if submitted:
    if not topic or not topic.strip():
        st.warning("Please enter a topic before running the pipeline.")
    else:
        try:
            run_pipeline(topic.strip())
            st.rerun()
        except Exception as e:
            st.session_state["running"] = False
            st.error(f"Pipeline failed: {e}")


# ----------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------
if st.session_state["report"]:
    st.markdown("---")

    tab_report, tab_critique, tab_sources = st.tabs(
        ["📄 Report", "🧐 Critique", "🗂️ Raw Research"]
    )

    with tab_report:
        st.markdown(f'<div class="report-box">{st.session_state["report"]}</div>', unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download report (.md)",
            data=st.session_state["report"],
            file_name="research_report.md",
            mime="text/markdown",
            use_container_width=False,
        )

    with tab_critique:
        feedback = st.session_state["feedback"] or ""
        # pull out a score like "Score: 7/10" if present, for a nice badge
        score_line = next((l for l in feedback.splitlines() if l.strip().lower().startswith("score")), None)
        if score_line:
            st.markdown(f'<span class="score-badge">{score_line.strip()}</span>', unsafe_allow_html=True)
            st.write("")
        st.markdown(feedback)

    with tab_sources:
        st.subheader("Search results")
        st.code(st.session_state["search_results"] or "", language="markdown")
        st.subheader("Scraped content")
        st.code(st.session_state["scraped_content"] or "", language="markdown")

else:
    st.info("Enter a topic above and click **Run 🚀** to generate a report.")