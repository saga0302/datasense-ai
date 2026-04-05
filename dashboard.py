import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="DataSense AI",
    page_icon="🔍",
    layout="wide"
)

# ── Load real data ────────────────────────────────────────────
@st.cache_data
def load_scored_orders():
    path = os.path.join(os.path.dirname(__file__), "data", "scored_orders.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data
def load_pipeline_status():
    try:
        from data.pipeline_runs import get_pipeline_failures, DEPENDENCY_MAP
        failures = get_pipeline_failures()
        failed_names = {p["name"] for p in failures}

        all_batches = [
            {"name": "instacart_earlymorning_batch", "time": "12am – 5am",  "db": "Instacart_Orders_DB"},
            {"name": "instacart_morning_batch",      "time": "6am – 11am",  "db": "Instacart_Orders_DB"},
            {"name": "instacart_afternoon_batch",    "time": "12pm – 5pm",  "db": "Instacart_Orders_DB"},
            {"name": "instacart_evening_batch",      "time": "6pm – 11pm",  "db": "Instacart_Orders_DB"},
        ]

        pipelines = []
        for b in all_batches:
            failed = b["name"] in failed_names
            detail = next((p for p in failures if p["name"] == b["name"]), {})
            pipelines.append({
                "name":    b["name"],
                "time":    b["time"],
                "db":      b["db"],
                "status":  "FAILED" if failed else "SUCCESS",
                "score":   detail.get("avg_anomaly_score", "—"),
                "orders":  detail.get("real_stats", {}).get("total_orders", "—"),
                "critical":detail.get("real_stats", {}).get("critical_orders", "—"),
            })
        return pipelines, failures
    except Exception:
        return [], []

df = load_scored_orders()
pipelines, failures = load_pipeline_status()

# ── Header ────────────────────────────────────────────────────
st.markdown("""
    <h1 style='text-align:center; color:#1E3A5F;'>
        🔍 DataSense AI
    </h1>
    <p style='text-align:center; color:#666; font-size:18px;'>
        Autonomous Pipeline Monitoring & Incident Response Agent
    </p>
    <hr>
""", unsafe_allow_html=True)

# ── Pipeline Status Grid ──────────────────────────────────────
st.subheader("📊 Pipeline Health Dashboard")

if pipelines:
    cols = st.columns(4)
    for i, p in enumerate(pipelines):
        with cols[i]:
            if p["status"] == "FAILED":
                st.error(f"🔴 **{p['name']}**")
            else:
                st.success(f"🟢 **{p['name']}**")
            st.caption(f"⏰ Window: {p['time']}")
            st.caption(f"🗄️ {p['db']}")
            if p["status"] == "FAILED":
                st.caption(f"📊 Avg score: {p['score']}")
                st.caption(f"🚨 Critical orders: {p['critical']:,}" if isinstance(p['critical'], int) else f"🚨 Critical: {p['critical']}")
else:
    st.info("No pipeline data found. Run models/train_severity.py first.")

st.markdown("---")

# ── Real metrics from scored_orders.csv ───────────────────────
col1, col2, col3, col4 = st.columns(4)

if not df.empty:
    total       = len(df)
    critical    = len(df[df["severity"] == "CRITICAL"])
    failed_ct   = len(failures)
    healthy_ct  = 4 - failed_ct
    downstream  = sum(
        len(p.get("real_stats", {})) for p in failures
    )

    col1.metric("Total Orders Analysed", f"{total:,}", "Real Instacart data")
    col2.metric("Critical Anomalies",    f"{critical:,}", f"{round(critical/total*100,1)}% of orders", delta_color="inverse")
    col3.metric("Failed Pipelines",      f"{failed_ct} of 4", delta=f"-{failed_ct}", delta_color="inverse")
    col4.metric("Healthy Pipelines",     f"{healthy_ct} of 4", "Running OK")
else:
    col1.metric("Total Pipelines", "4",  "Monitored")
    col2.metric("Failed",          str(len(failures)), delta=f"-{len(failures)}", delta_color="inverse")
    col3.metric("Downstream at Risk", "3", delta="-3", delta_color="inverse")
    col4.metric("Healthy", str(4 - len(failures)), "Running OK")

st.markdown("---")

# ── Failed pipeline detail ────────────────────────────────────
if failures:
    st.subheader("🚨 Failed Pipeline Detail")
    for p in failures:
        with st.expander(f"🔴 {p['name']} — avg anomaly score {p.get('avg_anomaly_score', 'N/A')}"):
            stats = p.get("real_stats", {})
            c1, c2, c3 = st.columns(3)
            c1.metric("Total orders",    f"{stats.get('total_orders', 0):,}")
            c2.metric("Critical orders", f"{stats.get('critical_orders', 0):,}")
            c3.metric("Critical rate",   f"{stats.get('critical_rate', 0)}%")
            st.error(p.get("error", ""))
    st.markdown("---")

# ── Run Agent Button ──────────────────────────────────────────
st.subheader("🤖 AI Agent Control")

if st.button("🚨 Run DataSense AI Agent", type="primary", use_container_width=True):

    with st.status("🔍 Agent is running...", expanded=True) as status:
        st.write("🔍 Node 1: Scanning Instacart pipeline batches...")
        time.sleep(1)
        st.write("🤖 Node 2: Classifying failures with Claude AI + RAG...")
        time.sleep(2)
        st.write("🔬 Node 2.5: Scoring anomalies with Isolation Forest...")
        time.sleep(1)
        st.write("🔗 Node 3: Investigating upstream dependencies...")
        time.sleep(1)
        st.write("📝 Node 4: Generating RCA report with Claude...")
        time.sleep(2)
        st.write("💾 Node 5: Saving report and sending notifications...")
        time.sleep(1)

        from agent.graph import datasense_agent
        result = datasense_agent.invoke({
            "failed_pipelines": [],
            "total_downstream_affected": [],
            "rca_report": "",
            "report_generated_at": "",
            "report_filename": "",
            "incident_data": {},
            "status": "starting"
        })

        status.update(label="✅ Agent Complete!", state="complete")

    st.success("✅ Incident report generated and saved!")

    r1, r2, r3 = st.columns(3)
    r1.metric("Failed Pipelines Found",      len(result["failed_pipelines"]))
    r2.metric("Downstream Systems at Risk",  len(result["total_downstream_affected"]))
    r3.metric("Report Status",               result["status"].upper())

    st.subheader("📄 AI-Generated Incident Report")
    st.markdown(result["rca_report"])

    st.subheader("⚠️ Downstream Systems Affected")
    for system in result["total_downstream_affected"]:
        st.warning(f"⚠️ {system}")

    st.cache_data.clear()

st.markdown("---")

# ── Past Incidents ─────────────────────────────────────────────
st.subheader("📁 Past Incidents")

if os.path.exists("incidents"):
    json_files = sorted(
        [f for f in os.listdir("incidents") if f.endswith(".json")],
        reverse=True
    )
    if json_files:
        for f in json_files[:5]:
            with open(f"incidents/{f}") as file:
                data = json.load(file)
            with st.expander(f"🗂️ {data['incident_id']} — {data['generated_at']}"):
                c1, c2 = st.columns(2)
                c1.metric("Failed Pipelines",   data["total_failed_pipelines"])
                c2.metric("Downstream Affected", data["total_downstream_affected"])
                st.json(data["pipelines"])
    else:
        st.info("No incidents recorded yet. Run the agent above!")
else:
    st.info("No incidents recorded yet. Run the agent above!")