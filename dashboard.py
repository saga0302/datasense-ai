import streamlit as st
import json
import os
import time
from datetime import datetime

st.set_page_config(
    page_title="DataSense AI",
    page_icon="🔍",
    layout="wide"
)

# ── Header ───────────────────────────────────────────────────
st.markdown("""
    <h1 style='text-align:center; color:#1E3A5F;'>
        🔍 DataSense AI
    </h1>
    <p style='text-align:center; color:#666; font-size:18px;'>
        Autonomous Pipeline Monitoring & Incident Response Agent
    </p>
    <hr>
""", unsafe_allow_html=True)

# ── Pipeline Status Grid ─────────────────────────────────────
st.subheader("📊 Pipeline Health Dashboard")

pipelines = [
    {"name": "sales_daily_etl",          "status": "FAILED",  "db": "Snowflake",  "last_run": "02:15 AM"},
    {"name": "inventory_sync",           "status": "SUCCESS", "db": "Azure SQL",  "last_run": "02:30 AM"},
    {"name": "customer_data_warehouse",  "status": "FAILED",  "db": "Snowflake",  "last_run": "01:45 AM"},
    {"name": "marketing_attribution",    "status": "SUCCESS", "db": "Azure SQL",  "last_run": "02:45 AM"},
    {"name": "finance_reporting_etl",    "status": "FAILED",  "db": "Snowflake",  "last_run": "01:30 AM"},
]

cols = st.columns(5)
for i, p in enumerate(pipelines):
    with cols[i]:
        if p["status"] == "FAILED":
            st.error(f"🔴 **{p['name']}**")
        else:
            st.success(f"🟢 **{p['name']}**")
        st.caption(f"🗄️ {p['db']}")
        st.caption(f"⏰ Last run: {p['last_run']}")

st.markdown("---")

# ── Metrics Row ──────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Pipelines",     "5",  "Monitored")
col2.metric("Failed",              "3",  delta="-3",  delta_color="inverse")
col3.metric("Downstream at Risk",  "9",  delta="-9",  delta_color="inverse")
col4.metric("Healthy",             "2",  "Running OK")

st.markdown("---")

# ── Run Agent Button ─────────────────────────────────────────
st.subheader("🤖 AI Agent Control")

if st.button("🚨 Run DataSense AI Agent", type="primary", use_container_width=True):

    with st.status("🔍 Agent is running...", expanded=True) as status:

        st.write("🔍 Node 1: Scanning pipelines for failures...")
        time.sleep(1)

        st.write("🤖 Node 2: Classifying failures with Claude AI...")
        time.sleep(2)

        st.write("🔗 Node 3: Investigating upstream dependencies...")
        time.sleep(1)

        st.write("📝 Node 4: Generating RCA report with Claude...")
        time.sleep(2)

        st.write("💾 Node 5: Saving report and sending notifications...")
        time.sleep(1)

        # Actually run the real agent
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

    # ── Results ──────────────────────────────────────────────
    st.success(f"✅ Incident report generated and saved!")

    r1, r2, r3 = st.columns(3)
    r1.metric("Failed Pipelines Found", len(result["failed_pipelines"]))
    r2.metric("Downstream Systems at Risk", len(result["total_downstream_affected"]))
    r3.metric("Report Status", result["status"].upper())

    # Show the report
    st.subheader("📄 AI-Generated Incident Report")
    st.markdown(result["rca_report"])

    # Show affected systems
    st.subheader("⚠️ Downstream Systems Affected")
    for system in result["total_downstream_affected"]:
        st.warning(f"⚠️ {system}")

st.markdown("---")

# ── Past Incidents ────────────────────────────────────────────
st.subheader("📁 Past Incidents")

if os.path.exists("incidents"):
    json_files = sorted(
        [f for f in os.listdir("incidents") if f.endswith(".json")],
        reverse=True
    )

    if json_files:
        for f in json_files[:5]:  # show last 5
            with open(f"incidents/{f}") as file:
                data = json.load(file)
            with st.expander(f"🗂️ {data['incident_id']} — {data['generated_at']}"):
                col1, col2 = st.columns(2)
                col1.metric("Failed Pipelines", data["total_failed_pipelines"])
                col2.metric("Downstream Affected", data["total_downstream_affected"])
                st.json(data["pipelines"])
    else:
        st.info("No incidents recorded yet. Run the agent above!")
else:
    st.info("No incidents recorded yet. Run the agent above!")