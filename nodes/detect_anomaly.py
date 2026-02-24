from datetime import datetime, timedelta
import random

# Mock pipeline data — simulates what we'd get from Azure SQL / Snowflake
# In production this would be a real database query
MOCK_PIPELINES = [
    {"pipeline_id": "PL_001", "name": "sales_daily_etl",         "status": "FAILED",  "error": "Connection timeout to source database",          "last_run": "2026-02-24 02:15:00", "database": "Snowflake"},
    {"pipeline_id": "PL_002", "name": "inventory_sync",          "status": "SUCCESS", "error": None,                                             "last_run": "2026-02-24 02:30:00", "database": "Azure SQL"},
    {"pipeline_id": "PL_003", "name": "customer_data_warehouse",  "status": "FAILED",  "error": "Schema mismatch: column 'revenue' not found",    "last_run": "2026-02-24 01:45:00", "database": "Snowflake"},
    {"pipeline_id": "PL_004", "name": "marketing_attribution",   "status": "SUCCESS", "error": None,                                             "last_run": "2026-02-24 02:45:00", "database": "Azure SQL"},
    {"pipeline_id": "PL_005", "name": "finance_reporting_etl",   "status": "FAILED",  "error": "Insufficient permissions on S3 bucket",          "last_run": "2026-02-24 01:30:00", "database": "Snowflake"},
]

def detect_anomaly(state: dict) -> dict:
    """
    Node 1: Scans all pipelines and returns any failures.
    Receives the agent state, adds failed pipelines to it, returns updated state.
    """
    print("\n🔍 Node 1: Scanning pipelines for failures...")

    # Filter only the failed pipelines
    failed_pipelines = [p for p in MOCK_PIPELINES if p["status"] == "FAILED"]

    if not failed_pipelines:
        print("✅ All pipelines healthy. No action needed.")
        return {**state, "failed_pipelines": [], "status": "healthy"}

    print(f"🚨 Found {len(failed_pipelines)} failed pipeline(s):")
    for p in failed_pipelines:
        print(f"   → {p['name']} | Error: {p['error']}")

    return {
        **state,
        "failed_pipelines": failed_pipelines,
        "status": "failures_detected"
    }