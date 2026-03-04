from utils.mcp_client import get_downstream_via_mcp
import json

def investigate_upstream(state: dict) -> dict:
    print("Node 3: Investigating dependencies via MCP...")

    failed_pipelines = state.get("failed_pipelines", [])
    total_downstream = set()

    for pipeline in failed_pipelines:
        name = pipeline["name"]
        print(f"Fetching dependencies for: {name} via MCP...")

        # Claude requests dependency data through MCP
        raw_deps = get_downstream_via_mcp(name)
        deps = json.loads(raw_deps)

        pipeline["dependencies"] = deps

        for d in deps.get("downstream_dependents", []):
            total_downstream.add(d)

        print(f"Upstream    : {', '.join(deps.get('upstream_sources', []))}")
        print(f"Downstream  : {', '.join(deps.get('downstream_dependents', []))}")

    print(f"Total unique downstream systems at risk: {len(total_downstream)}")

    return {
        **state,
        "failed_pipelines": failed_pipelines,
        "total_downstream_affected": list(total_downstream)
    }