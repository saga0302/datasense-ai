from datetime import datetime
import json
import os

def notify_and_save(state: dict) -> dict:
    """
    Node 5: Saves the incident report to a local file and simulates
    sending a Slack notification. In production this would write to
    Snowflake and call the Slack API.
    """
    print("\n💾 Node 5: Saving report and sending notifications...")

    report = state.get("rca_report", "")
    failed_pipelines = state.get("failed_pipelines", [])
    total_downstream = state.get("total_downstream_affected", [])
    generated_at = state.get("report_generated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Create incidents folder if it doesn't exist
    os.makedirs("incidents", exist_ok=True)

    # Save full RCA report as markdown file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"incidents/INC_{timestamp}.md"

    with open(report_filename, "w") as f:
        f.write(f"# Incident Report\n")
        f.write(f"**Generated At:** {generated_at}\n\n")
        f.write(report)

    print(f"   ✅ Report saved to: {report_filename}")

    # Save structured incident data as JSON
    json_filename = f"incidents/INC_{timestamp}.json"
    incident_data = {
        "incident_id": f"INC-{timestamp}",
        "generated_at": generated_at,
        "total_failed_pipelines": len(failed_pipelines),
        "total_downstream_affected": len(total_downstream),
        "downstream_systems": total_downstream,
        "pipelines": [
            {
                "name": p["name"],
                "error": p["error"],
                "failure_type": p.get("classification", {}).get("failure_type"),
                "severity": p.get("classification", {}).get("severity"),
                "estimated_fix_time": p.get("classification", {}).get("estimated_fix_time"),
            }
            for p in failed_pipelines
        ]
    }

    with open(json_filename, "w") as f:
        json.dump(incident_data, f, indent=2)

    print(f"   ✅ Incident data saved to: {json_filename}")

    # Simulate Slack notification
    print("\n   📲 Simulating Slack notification...")
    print("   ┌─────────────────────────────────────────────┐")
    print("   │  🚨 DATASENSE AI — PIPELINE ALERT           │")
    print("   │─────────────────────────────────────────────│")
    print(f"   │  Failed Pipelines : {len(failed_pipelines)} detected               │")
    print(f"   │  Downstream Risk  : {len(total_downstream)} systems affected        │")
    print(f"   │  Severity         : HIGH                    │")
    print(f"   │  Report           : {report_filename}  │")
    print("   │  → Full RCA report generated automatically  │")
    print("   └─────────────────────────────────────────────┘")

    return {
        **state,
        "report_filename": report_filename,
        "incident_data": incident_data,
        "status": "complete"
    }