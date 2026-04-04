from utils.mcp_client import scan_pipelines_via_mcp
import json

def detect_anomaly(state: dict) -> dict:
    print("Node 1: Scanning pipelines via MCP...")

    raw_data = scan_pipelines_via_mcp()

    # Guard against empty response
    if not raw_data or not raw_data.strip():
        print("   API mode — loading from pipeline_runs (MCP active on local)")
        from data.pipeline_runs import PIPELINE_FAILURES
        all_failed_pipelines = PIPELINE_FAILURES
    else:
        try:
            all_failed_pipelines = json.loads(raw_data)
        except json.JSONDecodeError:
            print("   API mode — loading from pipeline_runs (MCP active on local)")
            from data.pipeline_runs import PIPELINE_FAILURES
            all_failed_pipelines = PIPELINE_FAILURES

    if not all_failed_pipelines:
        print("   ℹ️  No failed pipelines detected")
        return {
            **state,
            "failed_pipelines": [],
            "status": "no_failures"
        }

    print(f"Found {len(all_failed_pipelines)} failed pipeline(s):")
    for p in all_failed_pipelines:
        print(f"   → {p['name']} | Score: {p.get('avg_anomaly_score', 'N/A')}")

    return {
        **state,
        "failed_pipelines": all_failed_pipelines,
        "status": "failures_detected"
    }