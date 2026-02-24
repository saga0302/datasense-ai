from nodes.detect_anomaly import detect_anomaly

# Start with an empty state — just like LangGraph will do
state = {}

# Run Node 1
result = detect_anomaly(state)

print("\n--- State after Node 1 ---")
print(f"Status: {result['status']}")
print(f"Failed pipelines found: {len(result['failed_pipelines'])}")