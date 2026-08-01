import streamlit as st
import requests
import json
import pandas as pd
import time

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Novetum Enterprise LLM & Agent Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Premium Enterprise CSS ──────────────────────────────────────────────────
# NOTE: Newer Streamlit versions render the page inside nested containers
# (stAppViewContainer / stMain / block-container) rather than relying on the
# old .stApp selector alone, and native widgets (tabs, subheaders, captions)
# carry their own theme colors that silently win if not explicitly overridden.
# Every rule below is written against the actual current container/text
# selectors, with !important where Streamlit's own generated classes would
# otherwise out-rank a plain selector. This is 100% CSS — no backend change.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Background — target every current Streamlit container layer ── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main .block-container {
    background: linear-gradient(160deg, #080a11 0%, #0d1117 55%, #0f1623 100%) !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
}
[data-testid="stSidebar"] {
    background: #0d1117 !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer { visibility: hidden; }

/* ── Force readable text color everywhere by default ── */
.stApp, .stApp p, .stApp span, .stApp label, .stApp li,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
[data-testid="stWidgetLabel"] p,
[data-testid="stText"] {
    color: #cbd5e1 !important;
}
h1, h2, h3, h4, h5, h6,
.stApp h1, .stApp h2, .stApp h3,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea {
    background: rgba(30,41,59,0.6) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #64748b !important;
}

/* ── Header Banner ── */
.nov-header {
    background: linear-gradient(105deg, #1a1040 0%, #230d6e 45%, #2d1278 100%);
    padding: 20px 28px;
    border-radius: 14px;
    border: 1px solid rgba(139,92,246,0.35);
    box-shadow: 0 8px 32px -8px rgba(99,102,241,0.35), 0 0 0 1px rgba(255,255,255,0.03);
    margin-bottom: 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.nov-title { margin:0; font-size:1.85rem; font-weight:800; color:#f1f5f9 !important; letter-spacing:-0.5px; }
.nov-sub   { margin:6px 0 0; color:#94a3b8 !important; font-size:0.88rem; font-weight:400; }
.status-pill {
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.45);
    color: #34d399 !important;
    padding: 6px 14px;
    border-radius: 999px;
    font-size:0.82rem;
    font-weight:600;
    display:flex; align-items:center; gap:7px;
    white-space: nowrap;
}
.pulse-dot {
    width:8px; height:8px;
    background:#10b981;
    border-radius:50%;
    animation: pulse 2s ease-in-out infinite;
    box-shadow: 0 0 0 0 rgba(16,185,129,0.6);
}
@keyframes pulse {
    0%   { box-shadow: 0 0 0 0   rgba(16,185,129,0.6); }
    70%  { box-shadow: 0 0 0 8px rgba(16,185,129,0.0); }
    100% { box-shadow: 0 0 0 0   rgba(16,185,129,0.0); }
}

/* ── Workflow Pipeline ── */
.wf-wrap {
    display:flex; flex-wrap:wrap; align-items:center;
    gap:6px;
    background: rgba(15,23,42,0.65);
    border:1px solid rgba(255,255,255,0.07);
    border-radius:12px;
    padding:14px 18px;
    margin-bottom:22px;
}
.wf-node {
    padding:7px 13px;
    border-radius:999px;
    font-size:0.8rem;
    font-weight:600;
    display:flex; align-items:center; gap:5px;
    transition: all 0.3s ease;
}
.wf-idle    { background:rgba(30,41,59,0.7);   color:#64748b !important; border:1px solid rgba(255,255,255,0.06); }
.wf-active  { background:rgba(99,102,241,0.18); color:#a5b4fc !important; border:1px solid rgba(99,102,241,0.5);
              box-shadow: 0 0 12px rgba(99,102,241,0.4); animation: glow 1.2s ease-in-out infinite alternate; }
.wf-done    { background:rgba(16,185,129,0.13); color:#34d399 !important; border:1px solid rgba(16,185,129,0.35); }
.wf-kb      { background:rgba(245,158,11,0.13); color:#fbbf24 !important; border:1px solid rgba(245,158,11,0.35); }
.wf-mcp     { background:rgba(59,130,246,0.13); color:#60a5fa !important; border:1px solid rgba(59,130,246,0.35); }
.wf-rag     { background:rgba(168,85,247,0.13); color:#c084fc !important; border:1px solid rgba(168,85,247,0.35); }
@keyframes glow {
    from { box-shadow: 0 0 6px rgba(99,102,241,0.4); }
    to   { box-shadow: 0 0 18px rgba(99,102,241,0.8); }
}
.wf-arrow { color:#475569 !important; font-size:0.9rem; padding:0 2px; }

/* ── Source Badges ── */
.badge {
    display:inline-flex; align-items:center; gap:5px;
    padding:3px 10px; border-radius:999px;
    font-size:0.72rem; font-weight:700;
    letter-spacing:0.3px;
    margin-right:6px;
}
.badge-kb  { background:rgba(245,158,11,0.15); color:#fbbf24 !important; border:1px solid rgba(245,158,11,0.3); }
.badge-mcp { background:rgba(59,130,246,0.15);  color:#60a5fa !important; border:1px solid rgba(59,130,246,0.3); }
.badge-rag { background:rgba(168,85,247,0.15); color:#c084fc !important; border:1px solid rgba(168,85,247,0.3); }
.badge-direct { background:rgba(16,185,129,0.12); color:#34d399 !important; border:1px solid rgba(16,185,129,0.28); }

/* ── Response Card ── */
.resp-card {
    background: rgba(30,41,59,0.5);
    backdrop-filter: blur(14px);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:12px;
    padding:18px 20px;
    margin-top:10px;
}

/* ── Context Output Card ── */
.ctx-card {
    background: #0a0c10;
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 10px;
    padding: 14px 16px;
    margin-top: 10px;
}
.ctx-label {
    font-size: 0.8rem;
    font-weight: 700;
    color: #6366f1 !important;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.ctx-pre {
    margin: 0;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 0.85rem;
    line-height: 1.65;
    color: #e2e8f0 !important;
    white-space: pre-wrap;
    word-break: break-word;
    background: transparent;
    border: none;
    padding: 0;
}
.resp-text { font-size:0.95rem; line-height:1.7; color:#cbd5e1 !important; }

/* ── Metric Cards ── */
div[data-testid="stMetricValue"] {
    font-size:1.65rem; font-weight:800;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
div[data-testid="stMetricLabel"] p {
    color: #94a3b8 !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-size: 0.75rem !important;
}
[data-testid="stMetric"] {
    background: rgba(30,41,59,0.55) !important;
    backdrop-filter: blur(12px);
    border-radius:12px !important;
    border:1px solid rgba(255,255,255,0.07) !important;
    padding:16px !important;
}

/* ── Eval Score Circles ── */
.eval-grid { display:flex; gap:16px; flex-wrap:wrap; margin-bottom:20px; }
.eval-card {
    flex:1; min-width:160px;
    background:rgba(30,41,59,0.5);
    border:1px solid rgba(255,255,255,0.07);
    border-radius:14px;
    padding:18px 14px;
    text-align:center;
    backdrop-filter:blur(12px);
}
.eval-score {
    font-size:2.4rem; font-weight:800;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.eval-label { font-size:0.8rem; color:#64748b !important; margin-top:4px; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; }
.eval-bar-wrap { height:5px; background:rgba(255,255,255,0.07); border-radius:999px; margin-top:12px; }
.eval-bar { height:5px; border-radius:999px; background: linear-gradient(90deg, #6366f1, #38bdf8); }

/* ── Trace Step Cards ── */
.trace-step {
    display:flex; gap:12px; align-items:flex-start;
    background:rgba(15,23,42,0.6);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:10px;
    padding:12px 14px;
    margin-bottom:8px;
}
.trace-icon { font-size:1.1rem; margin-top:2px; }
.trace-name { font-weight:700; color:#94a3b8 !important; font-size:0.82rem; letter-spacing:0.4px; text-transform:uppercase; }
.trace-out  { color:#cbd5e1 !important; font-size:0.88rem; margin-top:2px; }
.trace-ms   { margin-left:auto; font-size:0.78rem; color:#64748b !important; white-space:nowrap; padding-left:8px; }

/* ── KB Entries ── */
.kb-entry {
    display:flex; justify-content:space-between; align-items:flex-start;
    background:rgba(30,41,59,0.45);
    border:1px solid rgba(255,255,255,0.07);
    border-radius:10px;
    padding:14px 16px;
    margin-bottom:8px;
    gap:12px;
}
.kb-q { font-weight:600; color:#a5b4fc !important; font-size:0.9rem; }
.kb-a { color:#94a3b8 !important; font-size:0.84rem; margin-top:4px; }
.kb-tag { background:rgba(245,158,11,0.12); color:#fbbf24 !important; border:1px solid rgba(245,158,11,0.25);
          padding:2px 9px; border-radius:999px; font-size:0.72rem; font-weight:700; white-space:nowrap; }

/* ── Buttons ── */
.stButton>button {
    background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
    color:#fff !important; font-weight:700; border:none !important;
    border-radius:10px; padding:10px 22px;
    transition: all 0.25s ease;
    letter-spacing:0.3px;
}
.stButton>button:hover {
    transform:translateY(-2px);
    box-shadow:0 8px 24px rgba(99,102,241,0.4);
}
.stButton>button p { color:#fff !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    border-bottom: 1px solid rgba(255,255,255,0.08) !important;
    gap: 4px;
}
button[data-baseweb="tab"] {
    font-weight:600; font-size:0.88rem;
    border-radius:8px 8px 0 0 !important;
    background: transparent !important;
}
button[data-baseweb="tab"] p {
    color: #94a3b8 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: rgba(99,102,241,0.15) !important;
}
button[data-baseweb="tab"][aria-selected="true"] p {
    color: #a5b4fc !important;
    font-weight: 700 !important;
}
[data-baseweb="tab-highlight"] {
    background-color: #8b5cf6 !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(30,41,59,0.4) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary p {
    color: #cbd5e1 !important;
    font-weight: 600 !important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"] {
    background: rgba(30,41,59,0.4) !important;
    border-radius: 10px !important;
}

/* ── Alerts (success/error/warning/info) keep readable text ── */
[data-testid="stAlert"] p {
    color: inherit !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:rgba(30,41,59,0.3); }
::-webkit-scrollbar-thumb { background:rgba(99,102,241,0.4); border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ─── Helper: source badge (fuzzy match — works regardless of exact backend enum casing/naming) ──
def source_badge(intent: str) -> str:
    """
    Matches on keywords found anywhere in the intent string (case-insensitive),
    instead of requiring an exact match. This means it still labels correctly
    even if the backend returns 'knowledge_base', 'KNOWLEDGE_BASE', 'kb_lookup',
    etc. — anything containing 'knowledge' or 'kb' still gets the right badge.
    """
    text = (intent or "").lower()

    if "knowledge" in text or text == "kb" or "kb_" in text:
        return '<span class="badge badge-kb">📚 JSON Knowledge Base</span>'
    if "mcp" in text or "tool" in text:
        return '<span class="badge badge-mcp">⚡ MCP Execution</span>'
    if "rag" in text or "retriev" in text:
        return '<span class="badge badge-rag">🔍 Hybrid RAG</span>'
    return '<span class="badge badge-direct">💡 Direct Reasoning</span>'

# ─── Helper: workflow visualizer ────────────────────────────────────────────
NODE_ICONS = {
    "user":       "👤",
    "safety":     "🛡️",
    "memory":     "🧠",
    "knowledge":  "📚",
    "intent":     "🎯",
    "mcp":        "⚡",
    "reasoning":  "💡",
    "critic":     "🔍",
}

def render_workflow(active_node: str = "", completed_nodes: list = None, intent: str = ""):
    completed_nodes = completed_nodes or []
    nodes = [
        ("user",      "User Query"),
        ("safety",    "Safety"),
        ("memory",    "Memory"),
        ("knowledge", "Knowledge"),
        ("intent",    "Intent Router"),
        ("mcp",       "MCP / RAG"),
        ("reasoning", "Reasoning"),
        ("critic",    "Critic"),
    ]
    intent_text = (intent or "").lower()
    html = '<div class="wf-wrap">'
    for i, (key, label) in enumerate(nodes):
        if i > 0:
            html += '<div class="wf-arrow">➔</div>'
        if key in completed_nodes:
            css = "wf-done"
        elif key == active_node:
            css = "wf-active"
        elif key == "knowledge" and "knowledge" in intent_text:
            css = "wf-kb"
        elif key == "mcp" and ("mcp" in intent_text or "tool" in intent_text):
            css = "wf-mcp"
        elif key == "mcp" and ("rag" in intent_text or "retriev" in intent_text):
            css = "wf-rag"
        else:
            css = "wf-idle"
        html += f'<div class="wf-node {css}">{NODE_ICONS[key]} {label}</div>'
    html += '</div>'
    return html

# ─── Helper: trace step icon (fuzzy match on step_name keywords) ───────────
def step_icon(step_name: str) -> str:
    text = (step_name or "").lower()
    if "safety" in text or "guardrail" in text:
        return "🛡️"
    if "memory" in text:
        return "🧠"
    if "knowledge" in text or "kb" in text:
        return "📚"
    if "plan" in text or "intent" in text or "rout" in text:
        return "🎯"
    if "mcp" in text or "tool" in text:
        return "⚡"
    if "rag" in text or "retriev" in text:
        return "🔍"
    if "reason" in text:
        return "💡"
    if "critic" in text or "eval" in text:
        return "✅"
    return "⚙️"

# ─── Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nov-header">
    <div>
        <p class="nov-title">⚡ Novetum Enterprise LLM &amp; Agent Platform</p>
        <p class="nov-sub">LangGraph Stateful Graph &nbsp;|&nbsp; MCP Coding Agent &nbsp;|&nbsp; Hybrid RAG &nbsp;|&nbsp; JSON Knowledge Base &nbsp;|&nbsp; LLMOps &amp; Evals</p>
    </div>
    <div class="status-pill"><span class="pulse-dot"></span>Agent Online</div>
</div>
""", unsafe_allow_html=True)

# ─── Tabs ───────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "🤖  Agent Playground",
    "📊  LLMOps Observability",
    "🧪  Evaluation Suite",
    "📚  Knowledge Base",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — AGENT PLAYGROUND
# ════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    # Initial idle pipeline
    pipeline_ph = st.empty()
    pipeline_ph.markdown(render_workflow(), unsafe_allow_html=True)

    col_q, col_s = st.columns([3, 1])
    with col_q:
        user_query = st.text_input(
            "Query — algorithms, RAG, knowledge, or any code question:",
            value="Write python code for Two Sum algorithm",
            label_visibility="visible"
        )
    with col_s:
        session_id = st.text_input("Session ID:", value="session_novetum_01")

    run_btn = st.button("🚀  Execute LangGraph Workflow", use_container_width=True)

    result_ph  = st.empty()
    traces_ph  = st.empty()

    if run_btn and user_query:
        # Animate pipeline: step through nodes (cosmetic "in progress" indicator —
        # the real result and metrics come from the API call below)
        all_nodes = ["user","safety","memory","knowledge","intent","mcp","reasoning","critic"]
        done = []
        for node in all_nodes:
            pipeline_ph.markdown(render_workflow(active_node=node, completed_nodes=done), unsafe_allow_html=True)
            time.sleep(0.12)
            done.append(node)

        with st.spinner("Finalizing..."):
            try:
                res = requests.post(f"{API_BASE_URL}/api/chat",
                                    json={"query": user_query, "session_id": session_id})
            except Exception as e:
                pipeline_ph.markdown(render_workflow(completed_nodes=all_nodes), unsafe_allow_html=True)
                result_ph.error(f"Cannot reach backend — {e}")
                st.stop()

        pipeline_ph.markdown(render_workflow(completed_nodes=all_nodes), unsafe_allow_html=True)

        if res.status_code == 200:
            data   = res.json()
            intent = data.get("intent","")
            obs    = data.get("observability", {})
            steps  = obs.get("steps", [])

            # Re-render with intent colour
            pipeline_ph.markdown(
                render_workflow(completed_nodes=all_nodes, intent=intent),
                unsafe_allow_html=True
            )

            badge_html = source_badge(intent)
            response_text = data.get("response", "")
            context_text  = data.get("context",  "")
            critic_text   = data.get("critic",    "")

            with result_ph.container():
                st.markdown("---")
                col_r1, col_r2 = st.columns([2, 1])

                with col_r1:
                    st.markdown(f"""
                    <div class="resp-card">
                        <div style="margin-bottom:10px;">{badge_html}</div>
                        <div class="resp-text">{response_text}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if context_text:
                        st.markdown("""
                        <div class="ctx-card">
                            <div class="ctx-label">🔍 Retrieved Context / MCP Output</div>
                            <pre class="ctx-pre">{}</pre>
                        </div>
                        """.format(context_text.replace("<","&lt;").replace(">","&gt;")), unsafe_allow_html=True)

                with col_r2:
                    st.markdown("**📊 Run Metrics**")
                    m1, m2 = st.columns(2)
                    m1.metric("Latency (ms)",   f"{obs.get('latency_ms',0):.1f}")
                    m2.metric("Tokens",          obs.get("total_tokens", 0))
                    m3, m4 = st.columns(2)
                    m3.metric("Cost ($)",        f"${obs.get('estimated_cost_usd',0):.5f}")
                    m4.metric("Intent",          intent.replace("_"," ").title() if intent else "—")
                    st.markdown(f"**Critic:** `{critic_text}`")

            # Trace steps
            with traces_ph.container():
                with st.expander("🔬 Node Execution Trace", expanded=False):
                    if steps:
                        for step in steps:
                            icon = step_icon(step.get("step_name",""))
                            ms   = step.get("latency_ms", 0)
                            out  = step.get("step_output","")[:120]
                            st.markdown(f"""
                            <div class="trace-step">
                                <div class="trace-icon">{icon}</div>
                                <div style="flex:1">
                                    <div class="trace-name">{step.get("step_name","")}</div>
                                    <div class="trace-out">{out}</div>
                                </div>
                                <div class="trace-ms">{ms:.1f} ms</div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.info("No step-level trace data returned for this run.")
        else:
            result_ph.error(f"API Error {res.status_code}: {res.text}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — LLMOPS OBSERVABILITY
# ════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.subheader("LLMOps Tracing & Observability")
    if st.button("🔄  Refresh Logs"):
        try:
            res = requests.get(f"{API_BASE_URL}/api/observability/logs")
            if res.status_code == 200:
                obs_data = res.json()
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Total Requests", obs_data.get("total_requests",0))
                c2.metric("Total Tokens",   obs_data.get("total_tokens",0))
                c3.metric("Total Cost ($)", f"${obs_data.get('total_cost_usd',0):.5f}")
                c4.metric("Avg Latency",    f"{obs_data.get('avg_latency_ms',0):.1f} ms")

                st.markdown("### 📋 Trace Log Table")
                df = pd.DataFrame(obs_data.get("recent_traces",[]))
                if not df.empty:
                    keep = [c for c in ["trace_id","query","model_name","total_tokens","latency_ms","estimated_cost_usd","status"] if c in df.columns]
                    st.dataframe(df[keep] if keep else df, use_container_width=True)
                else:
                    st.info("No traces recorded yet. Execute a query in the Agent Playground.")
            else:
                st.error("Failed to fetch observability logs.")
        except Exception as e:
            st.warning(f"Connection error: {e}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — EVALUATION SUITE
# ════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.subheader("Enterprise Evaluation & Benchmark Suite")
    st.caption("Measures Answer Relevancy · Faithfulness · Context Precision · Accuracy · Latency")

    if st.button("🧪  Run Evaluation Benchmark", use_container_width=True):
        with st.spinner("Running benchmark suite..."):
            try:
                res = requests.post(f"{API_BASE_URL}/api/eval/run")
                if res.status_code == 200:
                    ev = res.json()

                    # Animated score cards
                    scores = [
                        ("Accuracy",           f"{ev.get('accuracy_percentage',0)}%",   ev.get('accuracy_percentage',0)/100),
                        ("Avg Faithfulness",   f"{ev.get('avg_faithfulness',0):.2f}",   ev.get('avg_faithfulness',0)),
                        ("Avg Relevancy",      f"{ev.get('avg_relevancy',0):.2f}",       ev.get('avg_relevancy',0)),
                        ("Avg Latency (ms)",   f"{ev.get('avg_latency_ms',0):.0f} ms",  min(ev.get('avg_latency_ms',0)/3000,1)),
                    ]
                    html_cards = '<div class="eval-grid">'
                    for label, val, pct in scores:
                        bar_w = int(max(0, min(pct, 1)) * 100)
                        html_cards += f"""
                        <div class="eval-card">
                            <div class="eval-score">{val}</div>
                            <div class="eval-label">{label}</div>
                            <div class="eval-bar-wrap"><div class="eval-bar" style="width:{bar_w}%"></div></div>
                        </div>"""
                    html_cards += '</div>'
                    st.markdown(html_cards, unsafe_allow_html=True)

                    c1, c2 = st.columns(2)
                    c1.metric("Passed Tests", ev.get("passed_cases",0))
                    c2.metric("Failed Tests", ev.get("failed_cases",0))

                    st.markdown("### 📋 Test Result Matrix")
                    st.dataframe(pd.DataFrame(ev.get("test_results",[])), use_container_width=True)
                else:
                    st.error("Evaluation run failed.")
            except Exception as e:
                st.warning(f"Connection error: {e}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — KNOWLEDGE BASE MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.subheader("📚 JSON Knowledge Base Management")

    col_add, col_list = st.columns([1, 2])

    with col_add:
        st.markdown("#### ➕ Add New Q&A Entry")
        new_q = st.text_input("Question:", key="kb_q")
        new_a = st.text_area("Answer:", key="kb_a", height=120)
        if st.button("💾  Save Entry", use_container_width=True):
            if new_q and new_a:
                try:
                    r = requests.post(f"{API_BASE_URL}/api/knowledge",
                                      json={"question": new_q, "answer": new_a})
                    if r.status_code == 200:
                        st.success("✅ Entry saved to Knowledge Base!")
                    else:
                        st.error("Failed to add entry.")
                except Exception as e:
                    st.warning(f"Server error: {e}")
            else:
                st.warning("Please fill in both fields.")

    with col_list:
        st.markdown("#### 📖 Stored Entries")
        try:
            r = requests.get(f"{API_BASE_URL}/api/knowledge")
            if r.status_code == 200:
                kb_entries = r.json()
                st.caption(f"Total entries: **{len(kb_entries)}**")
                search_kb = st.text_input("🔎 Filter:", key="kb_search", placeholder="Search questions or answers…")
                filtered  = [e for e in kb_entries
                             if search_kb.lower() in e.get('question','').lower()
                             or search_kb.lower() in e.get('answer','').lower()]

                if filtered:
                    for entry in filtered[:30]:
                        st.markdown(f"""
                        <div class="kb-entry">
                            <div style="flex:1">
                                <div class="kb-q">❓ {entry['question']}</div>
                                <div class="kb-a">{entry['answer'][:180]}{"…" if len(entry['answer'])>180 else ""}</div>
                            </div>
                            <div class="kb-tag">JSON</div>
                        </div>""", unsafe_allow_html=True)
                    if len(filtered) > 30:
                        st.caption(f"Showing 30 of {len(filtered)} matching entries.")
                else:
                    st.info("No entries match your filter." if search_kb else "Knowledge Base is empty.")
            else:
                st.error("Could not load Knowledge Base.")
        except Exception as e:
            st.warning(f"Could not connect to backend: {e}")