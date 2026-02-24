from nodes.detect_anomaly import detect_anomaly
from nodes.classify_failure import classify_failure
from nodes.investigate_upstream import investigate_upstream

state = {}
state = detect_anomaly(state)
state = classify_failure(state)
state = investigate_upstream(state)

print("\n--- State after Node 3 ---")
print(f"Total downstream systems at risk: {len(state['total_downstream_affected'])}")
print("Affected systems:")
for system in state["total_downstream_affected"]:
    print(f"   → {system}")