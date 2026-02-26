from agent.graph import datasense_agent

print("🚀 Starting DataSense AI Agent...\n")

# Run the compiled LangGraph agent
result = datasense_agent.invoke({
    "failed_pipelines": [],
    "total_downstream_affected": [],
    "rca_report": "",
    "report_generated_at": "",
    "report_filename": "",
    "incident_data": {},
    "status": "starting"
})

print("\n══════════════════════════════════════")
print(f"✅ Agent finished — Status: {result['status']}")
print(f"📁 Report: {result['report_filename']}")
print(f"🔥 Downstream systems at risk: {len(result['total_downstream_affected'])}")
print("══════════════════════════════════════")