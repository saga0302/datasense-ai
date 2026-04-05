from utils.mcp_client import get_downstream_via_mcp
import json

def investigate_upstream(state: dict) -> dict:
    print("Node 3: Investigating dependencies...")

    failed_pipelines = state.get("failed_pipelines", [])
    total_downstream = set()

    for pipeline in failed_pipelines:
        name = pipeline["name"]
        print(f"Fetching dependencies for: {name}...")

        raw_deps = get_downstream_via_mcp(name)

        # Guard against empty response
        if not raw_deps or not raw_deps.strip():
            print("   🔵 API mode — loading from DEPENDENCY_MAP")
            from data.pipeline_runs import DEPENDENCY_MAP
            deps = DEPENDENCY_MAP.get(name, {
                "upstream_sources": [],
                "downstream_dependents": [],
                "shared_infrastructure": []
            })
        else:
            try:
                deps = json.loads(raw_deps)
            except json.JSONDecodeError:
                print("   🔵 API mode — loading from DEPENDENCY_MAP")
                from data.pipeline_runs import DEPENDENCY_MAP
                deps = DEPENDENCY_MAP.get(name, {
                    "upstream_sources": [],
                    "downstream_dependents": [],
                    "shared_infrastructure": []
                })

        # Guard: ensure deps is always a dict not a string
        if not isinstance(deps, dict):
            try:
                deps = json.loads(deps)
            except Exception:
                deps = {
                    "upstream_sources": [],
                    "downstream_dependents": [],
                    "shared_infrastructure": []
                }

        pipeline["dependencies"] = deps

        for d in deps.get("downstream_dependents", []):
            total_downstream.add(d)

        print(f"Upstream  : {', '.join(deps.get('upstream_sources', []))}")
        print(f"Downstream: {', '.join(deps.get('downstream_dependents', []))}")

    print(f"Total unique downstream systems at risk: {len(total_downstream)}")

    return {
        **state,
        "failed_pipelines": failed_pipelines,
        "total_downstream_affected": list(total_downstream)
    }