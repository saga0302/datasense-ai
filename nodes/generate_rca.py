from utils.claude_client import ask_claude
from datetime import datetime

def generate_rca(state: dict) -> dict:
    """
    Node 4: Takes everything found in Nodes 1, 2, 3 and asks Claude
    to write a complete professional Root Cause Analysis report.
    """
    print("\n📝 Node 4: Generating RCA report with Claude AI...")

    failed_pipelines = state.get("failed_pipelines", [])
    total_downstream = state.get("total_downstream_affected", [])

    # Build a detailed summary of everything the agent found
    pipeline_summary = ""
    for p in failed_pipelines:
        c = p.get("classification", {})
        d = p.get("dependencies", {})
        pipeline_summary += f"""
Pipeline: {p['name']}
- Error: {p['error']}
- Failure Type: {c.get('failure_type', 'UNKNOWN')}
- Severity: {c.get('severity', 'UNKNOWN')}
- Business Impact: {c.get('business_impact', 'Unknown')}
- Estimated Fix Time: {c.get('estimated_fix_time', 'Unknown')}
- Upstream Sources: {', '.join(d.get('upstream_sources', []))}
- Downstream Dependents: {', '.join(d.get('downstream_dependents', []))}
"""

    prompt = f"""
You are a senior data reliability engineer writing a formal incident report for leadership.

Today's date: {datetime.now().strftime("%Y-%m-%d %H:%M")}

FAILED PIPELINES DETECTED:
{pipeline_summary}

TOTAL DOWNSTREAM SYSTEMS AT RISK: {len(total_downstream)}
Affected Systems: {', '.join(total_downstream)}

Write a complete, professional Root Cause Analysis (RCA) report with these exact sections:

1. EXECUTIVE SUMMARY (2-3 sentences for non-technical leadership)
2. INCIDENT OVERVIEW (what failed, when, how many systems affected)
3. ROOT CAUSE ANALYSIS (for each failed pipeline, explain the root cause)
4. BUSINESS IMPACT ASSESSMENT (what is at risk if not fixed)
5. RECOMMENDED ACTIONS (specific steps to fix each pipeline, in priority order)
6. PREVENTION RECOMMENDATIONS (how to prevent this in future)

Write in a professional tone suitable for a VP or CTO to read.
"""

    print("   → Sending all findings to Claude...")
    report = ask_claude(
        prompt=prompt,
        system="You are a senior data reliability engineer writing formal incident reports for executive leadership. Be precise, professional, and actionable."
    )

    print("   ✅ RCA report generated successfully!")

    return {
        **state,
        "rca_report": report,
        "report_generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "report_generated"
    }