from utils.mcp_client import scan_pipelines_via_mcp
import json

def detect_anomaly(state: dict) -> dict:
    print("Node 1: Scanning pipelines via MCP...")

    # Claude requests pipeline data through MCP — not hardcoded anymore
    raw_data = scan_pipelines_via_mcp()
    all_failed_pipelines = json.loads(raw_data)

    print(f"Found {len(all_failed_pipelines)} failed pipeline(s) via MCP:")
    for p in all_failed_pipelines:
        print(f"   → {p['name']} | Error: {p['error']}")

    return {
        **state,
        "failed_pipelines": all_failed_pipelines,
        "status": "failures_detected"
    }