import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import re
from datetime import datetime
from utils.claude_client import ask_claude

st.set_page_config(
    page_title="DataSense AI — Analyst",
    page_icon="🤖",
    layout="wide"
)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Load all data ─────────────────────────────────────────────────────────────
@st.cache_data
def load_scored_orders():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "scored_orders.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data
def load_processed_orders():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "processed_orders.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data
def load_latest_incident():
    incidents_dir = os.path.join(os.path.dirname(__file__), "..", "incidents")
    if not os.path.exists(incidents_dir):
        return None, None
    json_files = sorted([f for f in os.listdir(incidents_dir) if f.endswith(".json")], reverse=True)
    md_files   = sorted([f for f in os.listdir(incidents_dir) if f.endswith(".md")],   reverse=True)
    incident_data, incident_text = None, None
    if json_files:
        with open(os.path.join(incidents_dir, json_files[0])) as f:
            incident_data = json.load(f)
    if md_files:
        with open(os.path.join(incidents_dir, md_files[0])) as f:
            incident_text = f.read()
    return incident_data, incident_text

@st.cache_data
def load_pipeline_failures():
    try:
        from data.pipeline_runs import get_pipeline_failures, DEPENDENCY_MAP
        return get_pipeline_failures(), DEPENDENCY_MAP
    except Exception:
        return [], {}

df            = load_scored_orders()
processed_df  = load_processed_orders()
incident_data, incident_text = load_latest_incident()
pipeline_failures, dependency_map = load_pipeline_failures()

# ── Batch helper ──────────────────────────────────────────────────────────────
def add_batch_column(dataframe):
    if dataframe.empty or "order_hour_of_day" not in dataframe.columns:
        return dataframe
    bins   = [0, 5, 11, 17, 23]
    labels = ["Early morning (1-5am)", "Morning (6-11am)",
              "Afternoon (12-5pm)", "Evening (6-11pm)"]
    dataframe = dataframe.copy()
    dataframe["batch"] = pd.cut(
        dataframe["order_hour_of_day"],
        bins=bins, labels=labels, include_lowest=True)
    return dataframe

df_batched = add_batch_column(df)

# ── Build full project context ────────────────────────────────────────────────
def build_full_context():
    ctx = ""

    if not df.empty:
        total       = len(df)
        crit        = len(df[df["severity"]=="CRITICAL"])
        high        = len(df[df["severity"]=="HIGH"])
        med         = len(df[df["severity"]=="MEDIUM"])
        low         = len(df[df["severity"]=="LOW"])
        top_score   = round(df["anomaly_score"].max(), 3)
        top_order   = int(df.loc[df["anomaly_score"].idxmax(), "order_id"])
        avg_score   = round(df["anomaly_score"].mean(), 3)
        avg_cart    = round(df["cart_size"].mean(), 1)
        avg_reorder = round(df["reorder_rate"].mean(), 3)

        ctx += f"""
=== SCORED ORDERS DATA ===
Total orders analysed: {total:,}
CRITICAL: {crit:,} ({round(crit/total*100,1)}%)
HIGH:     {high:,} ({round(high/total*100,1)}%)
MEDIUM:   {med:,}  ({round(med/total*100,1)}%)
LOW:      {low:,}  ({round(low/total*100,1)}%)
Most anomalous order_id: {top_order} (score: {top_score})
Average anomaly score: {avg_score}
Average cart size: {avg_cart} items
Average reorder rate: {avg_reorder}
Failure threshold: 0.35
"""

    if not df_batched.empty:
        ctx += "\n=== BATCH BREAKDOWN ===\n"
        for label in ["Early morning (1-5am)","Morning (6-11am)","Afternoon (12-5pm)","Evening (6-11pm)"]:
            subset = df_batched[df_batched["batch"]==label]
            if subset.empty: continue
            avg  = round(subset["anomaly_score"].mean(), 3)
            crit = len(subset[subset["severity"]=="CRITICAL"])
            status = "FAILED" if avg >= 0.35 else "SUCCESS"
            ctx += f"{label}: {len(subset):,} orders | avg score {avg} | {crit} CRITICAL | {status}\n"

    if pipeline_failures:
        ctx += "\n=== FAILED PIPELINE RUNS ===\n"
        for p in pipeline_failures:
            ctx += f"Pipeline: {p['name']}\n"
            ctx += f"Status: {p['status']}\n"
            ctx += f"Avg anomaly score: {p.get('avg_anomaly_score','N/A')}\n"
            ctx += f"Error: {p.get('error','N/A')}\n"
            stats = p.get("real_stats", {})
            if stats:
                ctx += f"Critical orders: {stats.get('critical_orders','N/A'):,}\n"
                ctx += f"Critical rate: {stats.get('critical_rate','N/A')}%\n"
            ctx += "\n"

    if dependency_map:
        ctx += "\n=== PIPELINE DEPENDENCIES ===\n"
        for name, deps in dependency_map.items():
            ctx += f"{name}:\n"
            ctx += f"  Upstream: {', '.join(deps.get('upstream_sources',[]))}\n"
            ctx += f"  Downstream: {', '.join(deps.get('downstream_dependents',[]))}\n"

    if incident_text:
        ctx += f"\n=== LATEST INCIDENT REPORT (truncated) ===\n"
        ctx += incident_text[:4000]

    return ctx

FULL_CONTEXT = build_full_context()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("DataSense AI")
    st.divider()
    st.markdown("**Example questions:**")
    st.markdown("- What happened in the latest run?")
    st.markdown("- How many orders in each batch?")
    st.markdown("- Which batch failed and why?")
    st.markdown("- Show me the trend by hour")
    st.markdown("- Compare time windows")
    st.markdown("- Predict tomorrow's risk")
    st.markdown("- Show most anomalous orders")
    st.markdown("- Tell me about order 2008596")
    st.markdown("- What does the incident report say?")
    st.markdown("- What are the downstream systems at risk?")
    st.markdown("- What is the ML model and how does it work?")
    st.divider()
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption(f"Orders: {len(df):,}" if not df.empty else "No data")
    if incident_data:
        st.caption(f"Incident: {incident_data.get('incident_id','N/A')}")
    if pipeline_failures:
        st.caption(f"Failed pipelines: {len(pipeline_failures)}")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🤖 DataSense AI — Conversational Analyst")
st.caption("Ask anything about your Instacart pipeline data, ML model, or incident reports")

# ── Intent router ─────────────────────────────────────────────────────────────
def route_intent(question: str) -> str:
    prompt = f"""Classify this question into exactly one category.
Return ONLY the category word, nothing else.

Categories:
- REPORT      (latest run, what happened, current status, summary)
- TREND       (over time, by hour, pattern, history)
- COMPARISON  (compare, vs, difference, better or worse)
- PREDICTION  (will, predict, forecast, tomorrow, future risk)
- ANOMALY     (most anomalous, worst orders, top anomalies)
- INCIDENT    (incident report, RCA, root cause, what was filed)
- ORDER       (specific order number mentioned e.g. order 2008596)
- BATCH       (orders per batch, how many in each window, batch sizes)
- PIPELINE    (which pipeline failed, pipeline status, dependencies, downstream)
- MODEL       (how does the ML work, Isolation Forest, anomaly score, features)
- GENERAL     (anything else about the project)

Question: {question}

Category:"""
    result = ask_claude(prompt, system="You are a classifier. Return only one word.")
    return result.strip().upper()

# ── Chart builders ────────────────────────────────────────────────────────────
def severity_bar_chart():
    if df.empty: return None
    counts = df["severity"].value_counts().reset_index()
    counts.columns = ["Severity","Orders"]
    counts["rank"] = counts["Severity"].map({"CRITICAL":0,"HIGH":1,"MEDIUM":2,"LOW":3})
    counts = counts.sort_values("rank")
    fig = px.bar(counts, x="Severity", y="Orders", color="Severity",
                 color_discrete_map={"CRITICAL":"#E24B4A","HIGH":"#EF9F27","MEDIUM":"#378ADD","LOW":"#639922"},
                 title="Severity distribution — all orders")
    fig.update_layout(showlegend=False, height=350)
    return fig

def hourly_trend_chart():
    if df.empty: return None
    hourly = df.groupby("order_hour_of_day").agg(
        avg_score=("anomaly_score","mean")).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hourly["order_hour_of_day"], y=hourly["avg_score"],
        mode="lines+markers", name="Avg anomaly score",
        line=dict(color="#378ADD", width=2)))
    fig.add_hline(y=0.35, line_dash="dash", line_color="#E24B4A",
                  annotation_text="Failure threshold (0.35)")
    fig.update_layout(title="Anomaly score by hour of day",
                      xaxis_title="Hour (0-23)",
                      yaxis_title="Avg anomaly score", height=350)
    return fig

def batch_bar_chart():
    if df_batched.empty: return None
    rows = []
    for label in ["Early morning (1-5am)","Morning (6-11am)","Afternoon (12-5pm)","Evening (6-11pm)"]:
        subset = df_batched[df_batched["batch"]==label]
        if subset.empty: continue
        avg = round(subset["anomaly_score"].mean(),3)
        rows.append({
            "Batch": label,
            "Total orders": len(subset),
            "Avg score": avg,
            "Status": "FAILED" if avg >= 0.35 else "SUCCESS"
        })
    bdf = pd.DataFrame(rows)
    fig = px.bar(bdf, x="Batch", y="Total orders", color="Status",
                 color_discrete_map={"FAILED":"#E24B4A","SUCCESS":"#639922"},
                 text="Total orders",
                 title="Orders per batch window")
    fig.update_traces(textposition="outside")
    fig.update_layout(height=350)
    return fig

def comparison_chart():
    if df_batched.empty: return None
    rows = []
    for label in ["Early morning (1-5am)","Morning (6-11am)","Afternoon (12-5pm)","Evening (6-11pm)"]:
        subset = df_batched[df_batched["batch"]==label]
        if subset.empty: continue
        rows.append({
            "Window": label,
            "Critical %": round((subset["severity"]=="CRITICAL").sum()/len(subset)*100,1),
            "Avg score": round(subset["anomaly_score"].mean(),3)
        })
    cdf = pd.DataFrame(rows)
    fig = px.bar(cdf, x="Window", y="Critical %", color="Avg score",
                 color_continuous_scale=["#639922","#EF9F27","#E24B4A"],
                 title="Critical order rate by time window")
    fig.update_layout(height=350)
    return fig

def gauge_chart():
    if df.empty: return None
    avg_score = round(df["anomaly_score"].mean(),3)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(avg_score*100,1),
        title={"text":"Pipeline anomaly risk"},
        gauge={"axis":{"range":[0,100]},"bar":{"color":"#378ADD"},
               "steps":[{"range":[0,25],"color":"#EAF3DE"},
                        {"range":[25,45],"color":"#FAEEDA"},
                        {"range":[45,100],"color":"#FAECE7"}],
               "threshold":{"line":{"color":"#E24B4A","width":4},
                            "thickness":0.75,"value":35}}))
    fig.update_layout(height=350)
    return fig

def anomaly_scatter_chart():
    if df.empty: return None
    top10 = df.nlargest(10,"anomaly_score")[
        ["order_id","anomaly_score","severity","cart_size","reorder_rate","order_hour_of_day"]
    ].copy()
    fig = px.scatter(top10, x="cart_size", y="anomaly_score",
                     color="severity", size="anomaly_score",
                     hover_data=["order_id","reorder_rate"],
                     color_discrete_map={"CRITICAL":"#E24B4A","HIGH":"#EF9F27"},
                     title="Top 10 most anomalous orders")
    fig.update_layout(height=350)
    return fig

# ── Universal response function ───────────────────────────────────────────────
def get_response(question: str) -> tuple:
    if df.empty:
        return "No data found. Run models/train_severity.py first.", None

    intent = route_intent(question)
    chart  = None

    # Pick the right chart for the intent
    if   intent == "REPORT":     chart = severity_bar_chart()
    elif intent == "TREND":      chart = hourly_trend_chart()
    elif intent == "COMPARISON": chart = comparison_chart()
    elif intent == "PREDICTION": chart = gauge_chart()
    elif intent == "ANOMALY":    chart = anomaly_scatter_chart()
    elif intent == "BATCH":      chart = batch_bar_chart()

    # Handle order lookup
    order_context = ""
    if intent == "ORDER":
        numbers = re.findall(r'\b\d{5,7}\b', question)
        if numbers:
            order_id  = int(numbers[0])
            order_row = df[df["order_id"] == order_id]
            if not order_row.empty:
                row = order_row.iloc[0]
                order_context = f"""
=== SPECIFIC ORDER DETAIL ===
Order ID: {int(row['order_id'])}
Anomaly score: {round(row['anomaly_score'],3)} / 1.000
Severity: {row['severity']}
Cart size: {int(row['cart_size'])} items
Reorder rate: {round(row['reorder_rate']*100,1)}%
Cart deviation from user baseline: {round(row['cart_deviation'],2)} std devs
Reorder deviation from user baseline: {round(row['reorder_deviation'],3)}
Days since prior order: {int(row['days_since_prior_order'])} days
Order hour: {int(row['order_hour_of_day'])}:00
Is first order: {'Yes' if row['is_first_order']==1 else 'No'}
User total orders ever: {int(row['user_total_orders'])}
User avg cart size: {round(row['user_avg_cart'],1)} items
User avg reorder rate: {round(row['user_avg_reorder'],3)}
Unique departments: {int(row['unique_departments'])}
"""

    # Build conversation history for context
    history = ""
    for msg in st.session_state.messages[-6:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role}: {msg['content']}\n"

    # Universal Claude prompt with all data
    prompt = f"""You are DataSense AI — an intelligent data reliability analyst for Instacart.
You have access to all pipeline data, ML model results, batch breakdowns, and incident reports.

=== FULL PROJECT DATA ===
{FULL_CONTEXT}
{order_context}

=== CONVERSATION HISTORY ===
{history}

=== CURRENT QUESTION ===
{question}

=== INSTRUCTIONS ===
Answer the question directly and specifically using the data above.
- Use real numbers from the data
- If asked about batches: state exact order counts per batch
- If asked about a specific order: give complete feature breakdown
- If asked about the incident report: reference specific findings
- If asked about the ML model: explain Isolation Forest in plain English
- If asked about pipelines: mention which failed and the downstream impact
- Keep response to 4-6 sentences unless the question needs more detail
- Never say you cannot access data — all data is provided above
"""

    response = ask_claude(prompt)
    return response, chart

# ── Chat history ──────────────────────────────────────────────────────────────
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("chart"):
            st.plotly_chart(msg["chart"], use_container_width=True,
                            key=f"chart_{i}")

# ── Text input ────────────────────────────────────────────────────────────────
question = st.chat_input("Ask anything about your pipeline data...")

if question:
    st.session_state.messages.append({"role":"user","content":question})

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Analysing..."):
            response, chart = get_response(question)
        st.write(response)
        if chart:
            st.plotly_chart(chart, use_container_width=True,
                            key=f"chart_new_{len(st.session_state.messages)}")

    st.session_state.messages.append({
        "role":"assistant","content":response,"chart":chart})