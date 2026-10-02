import uuid

import streamlit as st

from src.graph.graph import build_graph
from src.state.defaults import create_initial_state


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #777;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    .agent-box {
        padding: 12px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 8px;
    }

    .agent-active {
        font-weight: 700;
        border: 2px solid #4CAF50;
    }

    .metric-label {
        font-size: 0.8rem;
        color: #777;
    }

    .source-box {
        padding: 10px;
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "running" not in st.session_state:
    st.session_state.running = False

if "result" not in st.session_state:
    st.session_state.result = None

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "events" not in st.session_state:
    st.session_state.events = []

if "query" not in st.session_state:
    st.session_state.query = ""

if "submitted_query" not in st.session_state:
    st.session_state.submitted_query = ""


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🔎 Multi-Agent Research System</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    A LangGraph-powered multi-agent system for web research,
    evidence analysis, critical validation, and answer synthesis.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ System")

    st.markdown("### Agent Architecture")

    st.markdown(
        """
        **Supervisor**
        → Coordinates workflow

        **Researcher**
        → Searches and fetches web sources

        **Analyst**
        → Analyzes collected evidence

        **Critic**
        → Validates evidence and identifies gaps

        **Synthesis**
        → Produces the final answer
        """
    )

    st.divider()

    st.markdown("### Workflow")

    st.code(
        """
START        
    ↓    
Supervisor
    ↓
Researcher
    ↓
Analyst
    ↓
Critic
    ↓
Supervisor
    ↓
Synthesis
    ↓
END
        """,
        language="text",
    )

    st.divider()

    st.caption(
        "Powered by LangGraph + Gemini"
    )


# ============================================================
# AGENT DISPLAY HELPERS
# ============================================================

agent_order = [
    "supervisor",
    "researcher",
    "analyst",
    "critic",
    "synthesis",
]


agent_labels = {
    "supervisor": "🧠 Supervisor",
    "researcher": "🌐 Researcher",
    "analyst": "📊 Analyst",
    "critic": "🔍 Critic",
    "synthesis": "✍️ Synthesis",
}


agent_descriptions = {
    "supervisor": "Coordinates the workflow",
    "researcher": "Searches and gathers web evidence",
    "analyst": "Analyzes collected research",
    "critic": "Validates evidence and checks gaps",
    "synthesis": "Generates the final answer",
}


# ============================================================
# QUERY INPUT
# ============================================================

query = st.chat_input(
    "Enter your research question..."
)


# ============================================================
# DISPLAY CURRENT QUERY
# ============================================================

if query:

    st.session_state.query = query.strip()
    st.session_state.submitted_query = query.strip()

if st.session_state.submitted_query:

    st.chat_message("user").write(
        st.session_state.submitted_query
    )


# ============================================================
# START RESEARCH
# ============================================================

if query:

    if not query.strip():

        st.warning(
            "Please enter a research question first."
        )

        st.stop()

    st.session_state.running = True
    st.session_state.result = None
    st.session_state.events = []

    # Create a unique thread for this research execution.
    thread_id = str(uuid.uuid4())

    st.session_state.thread_id = thread_id

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = create_initial_state(
        query.strip()
    )

    # ========================================================
    # LAYOUT
    # ========================================================

    workflow_column, details_column = st.columns(
        [1, 2],
        gap="large",
    )

    # ========================================================
    # WORKFLOW PANEL
    # ========================================================

    with workflow_column:

        st.subheader("Agent Workflow")

        workflow_placeholder = st.empty()

    # ========================================================
    # DETAILS PANEL
    # ========================================================

    with details_column:

        st.subheader("Execution")

        status_placeholder = st.empty()

        progress_placeholder = st.empty()

        log_placeholder = st.empty()

    # ========================================================
    # GRAPH EXECUTION
    # ========================================================

    final_state = None

    try:

        graph = build_graph()

        event_history = []

        for event in graph.stream(
            initial_state,
            config=config,
            stream_mode="values",
        ):

            final_state = event

            current_agent = event.get(
                "current_agent",
                "",
            )

            iteration = event.get(
                "iteration",
                0,
            )

            research_round = event.get(
                "research_round",
                0,
            )

            tool_calls = event.get(
                "tool_calls",
                0,
            )

            event_history.append(
                {
                    "agent": current_agent,
                    "iteration": iteration,
                    "research_round": research_round,
                    "tool_calls": tool_calls,
                }
            )

            st.session_state.events = event_history

            # =================================================
            # UPDATE WORKFLOW UI
            # =================================================

            workflow_html = ""

            for agent in agent_order:

                is_current = (
                    agent == current_agent
                )

                previous_agent = (
                    agent in [
                        item["agent"]
                        for item in event_history[:-1]
                    ]
                )

                if is_current:

                    icon = "🟢"

                    css_class = (
                        "agent-box agent-active"
                    )

                    state_text = "Running"

                elif previous_agent:

                    icon = "✅"

                    css_class = "agent-box"

                    state_text = "Completed"

                else:

                    icon = "⚪"

                    css_class = "agent-box"

                    state_text = "Waiting"

                workflow_html += f"""
                <div class="{css_class}">
                    <strong>
                        {icon} {agent_labels[agent]}
                    </strong>
                    <br>
                    <small>
                        {agent_descriptions[agent]}
                    </small>
                    <br>
                    <small>
                        {state_text}
                    </small>
                </div>
                """

            workflow_placeholder.markdown(
                workflow_html,
                unsafe_allow_html=True,
            )

            # =================================================
            # STATUS
            # =================================================

            status_placeholder.info(
                f"Current Agent: "
                f"**{agent_labels.get(current_agent, current_agent)}**"
            )

            progress_placeholder.progress(
                min(
                    iteration / 15,
                    1.0,
                )
            )

            # =================================================
            # EVENT LOG
            # =================================================

            log_text = "\n".join(
                [
                    (
                        f"{index + 1}. "
                        f"{agent_labels.get(item['agent'], item['agent'])}"
                        f" — "
                        f"Iteration {item['iteration']}"
                    )
                    for index, item
                    in enumerate(event_history)
                ]
            )

            log_placeholder.code(
                log_text,
                language="text",
            )

        # ====================================================
        # EXECUTION COMPLETED
        # ====================================================

        st.session_state.result = final_state
        st.session_state.running = False

        status_placeholder.success(
            "Research completed successfully."
        )

        progress_placeholder.progress(1.0)

    except Exception as e:

        st.session_state.running = False

        status_placeholder.error(
            "Research execution failed."
        )

        st.exception(e)

        st.stop()


# ============================================================
# DISPLAY FINAL RESULT
# ============================================================

if st.session_state.result:

    state = st.session_state.result

    st.divider()

    st.header("📄 Final Answer")

    final_answer = state.get(
        "final_answer",
        "",
    )

    if final_answer:

        st.markdown(final_answer)

    else:

        st.warning(
            "No final answer was generated."
        )

    # ========================================================
    # FINAL METRICS
    # ========================================================

    st.divider()

    st.subheader("📈 Research Metrics")

    metric_columns = st.columns(4)

    metric_columns[0].metric(
        "Iterations",
        state.get("iteration", 0),
    )

    metric_columns[1].metric(
        "Research Rounds",
        state.get("research_round", 0),
    )

    metric_columns[2].metric(
        "Tool Calls",
        state.get("tool_calls", 0),
    )

    metric_columns[3].metric(
        "Sources",
        len(
            state.get(
                "sources",
                [],
            )
        ),
    )

    # ========================================================
    # RESEARCH RESULTS
    # ========================================================

    research_results = state.get(
        "research_results",
        [],
    )

    if research_results:

        st.divider()

        st.subheader(
            f"🌐 Research Sources ({len(research_results)})"
        )

        for index, result in enumerate(
            research_results,
            start=1,
        ):

            title = result.get(
                "title",
                "Untitled Source",
            )

            url = result.get(
                "url",
                "",
            )

            content = result.get(
                "content",
                "",
            )

            with st.expander(
                f"{index}. {title}"
            ):

                if url:

                    st.markdown(
                        f"**URL:** {url}"
                    )

                if content:

                    st.write(content)

    # ========================================================
    # ANALYSIS
    # ========================================================

    analysis = state.get(
        "analysis",
        "",
    )

    if analysis:

        st.divider()

        with st.expander(
            "📊 View Analyst Analysis",
            expanded=False,
        ):

            st.markdown(analysis)

    # ========================================================
    # CRITIQUE
    # ========================================================

    critique = state.get(
        "critique",
        "",
    )

    if critique:

        st.divider()

        with st.expander(
            "🔍 View Critic Evaluation",
            expanded=False,
        ):

            critique_passed = state.get(
                "critique_passed",
                False,
            )

            if critique_passed:

                st.success(
                    "Critic decision: PASS"
                )

            else:

                st.warning(
                    "Critic decision: RESEARCH REQUIRED"
                )

            st.markdown(critique)
