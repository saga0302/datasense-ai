from nodes.detect_anomaly import detect_anomaly
from nodes.classify_failure import classify_failure
from nodes.investigate_upstream import investigate_upstream
from nodes.generate_rca import generate_rca
from nodes.notify_and_save import notify_and_save

state = {}
state = detect_anomaly(state)
state = classify_failure(state)
state = investigate_upstream(state)
state = generate_rca(state)
state = notify_and_save(state)

print(f"\n✅ AGENT COMPLETE — Status: {state['status']}")
print(f"📁 Report saved to: {state['report_filename']}")