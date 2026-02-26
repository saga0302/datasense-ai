from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Any
from nodes.detect_anomaly import detect_anomaly
from nodes.classify_failure import classify_failure
from nodes.investigate_upstream import investigate_upstream
from nodes.generate_rca import generate_rca
from nodes.notify_and_save import notify_and_save

# ── 1. Define the State ──────────────────────────────────────
# This is the exact shape of the dictionary passed between nodes
class AgentState(TypedDict):
    failed_pipelines: List[Any]
    total_downstream_affected: List[str]
    rca_report: str
    report_generated_at: str
    report_filename: str
    incident_data: dict
    status: str

# ── 2. Build the Graph ───────────────────────────────────────
def build_graph():
    graph = StateGraph(AgentState)

    # Add all 5 nodes
    graph.add_node("detect_anomaly",       detect_anomaly)
    graph.add_node("classify_failure",     classify_failure)
    graph.add_node("investigate_upstream", investigate_upstream)
    graph.add_node("generate_rca",         generate_rca)
    graph.add_node("notify_and_save",      notify_and_save)

    # Connect them in order with edges
    graph.set_entry_point("detect_anomaly")
    graph.add_edge("detect_anomaly",       "classify_failure")
    graph.add_edge("classify_failure",     "investigate_upstream")
    graph.add_edge("investigate_upstream", "generate_rca")
    graph.add_edge("generate_rca",         "notify_and_save")
    graph.add_edge("notify_and_save",      END)

    return graph.compile()

# ── 3. The compiled agent — ready to run ────────────────────
datasense_agent = build_graph()