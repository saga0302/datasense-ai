from nodes.detect_anomaly import detect_anomaly
from nodes.classify_failure import classify_failure

# Run Node 1
state = {}
state = detect_anomaly(state)

# Run Node 2
state = classify_failure(state)

print("\n--- State after Node 2 ---")
for p in state["failed_pipelines"]:
    print(f"\nPipeline: {p['name']}")
    print(f"  Failure Type : {p['classification']['failure_type']}")
    print(f"  Severity     : {p['classification']['severity']}")
    print(f"  Business Impact: {p['classification']['business_impact']}")
    print(f"  Fix Time     : {p['classification']['estimated_fix_time']}")