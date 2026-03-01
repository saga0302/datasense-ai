import pytest
from nodes.detect_anomaly import detect_anomaly
from nodes.investigate_upstream import investigate_upstream

# ── Test 1 ───────────────────────────────────────────────────
def test_detect_anomaly_finds_failures():
    """Node 1 should find exactly 3 failed pipelines"""
    state = {}
    result = detect_anomaly(state)

    assert result["status"] == "failures_detected"
    assert len(result["failed_pipelines"]) == 3
    assert all(p["status"] == "FAILED" for p in result["failed_pipelines"])

# ── Test 2 ───────────────────────────────────────────────────
def test_detect_anomaly_state_preserved():
    """Node 1 should preserve any existing state keys"""
    state = {"existing_key": "existing_value"}
    result = detect_anomaly(state)

    assert result["existing_key"] == "existing_value"

# ── Test 3 ───────────────────────────────────────────────────
def test_failed_pipelines_have_required_fields():
    """Every failed pipeline must have name, error, status fields"""
    state = {}
    result = detect_anomaly(state)

    for pipeline in result["failed_pipelines"]:
        assert "name" in pipeline
        assert "error" in pipeline
        assert "status" in pipeline
        assert pipeline["error"] is not None

# ── Test 4 ───────────────────────────────────────────────────
def test_investigate_upstream_adds_dependencies():
    """Node 3 should add dependency info to each failed pipeline"""
    state = {
        "failed_pipelines": [
            {"pipeline_id": "PL_001", "name": "sales_daily_etl",
             "status": "FAILED", "error": "timeout",
             "last_run": "2026-02-24", "database": "Snowflake"}
        ],
        "status": "failures_detected"
    }
    result = investigate_upstream(state)

    pipeline = result["failed_pipelines"][0]
    assert "dependencies" in pipeline
    assert "downstream_dependents" in pipeline["dependencies"]
    assert "upstream_sources" in pipeline["dependencies"]

# ── Test 5 ───────────────────────────────────────────────────
def test_investigate_upstream_counts_downstream():
    """Node 3 should correctly count total downstream systems"""
    state = {
        "failed_pipelines": [
            {"pipeline_id": "PL_001", "name": "sales_daily_etl",
             "status": "FAILED", "error": "timeout",
             "last_run": "2026-02-24", "database": "Snowflake"}
        ],
        "status": "failures_detected"
    }
    result = investigate_upstream(state)

    assert "total_downstream_affected" in result
    assert len(result["total_downstream_affected"]) > 0