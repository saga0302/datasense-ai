from nodes.detect_anomaly import detect_anomaly
from nodes.classify_failure import classify_failure
from nodes.investigate_upstream import investigate_upstream
from nodes.generate_rca import generate_rca

state = {}
state = detect_anomaly(state)
state = classify_failure(state)
state = investigate_upstream(state)
state = generate_rca(state)

print("\n--- INCIDENT REPORT ---")
print(state["rca_report"])