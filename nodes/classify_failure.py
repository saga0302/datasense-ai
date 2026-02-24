from utils.claude_client import ask_claude
import json

def classify_failure(state: dict) -> dict:
    """
    Node 2: Takes each failed pipeline and asks Claude to classify the failure type.
    Claude reads the error message and returns structured JSON with classification.
    """
    print("\n🤖 Node 2: Classifying failures with Claude AI...")

    failed_pipelines = state.get("failed_pipelines", [])
    classified = []

    for pipeline in failed_pipelines:
        print(f"   → Classifying: {pipeline['name']}...")

        # This is prompt engineering — we give Claude a role, context, and strict output format
        prompt = f"""
You are analyzing a data pipeline failure. Classify this failure and return ONLY a JSON object, no other text.

Pipeline Name: {pipeline['name']}
Error Message: {pipeline['error']}
Database: {pipeline['database']}

Return this exact JSON structure:
{{
    "failure_type": "one of: CONNECTION_ERROR, SCHEMA_ERROR, PERMISSION_ERROR, DATA_QUALITY_ERROR, TIMEOUT_ERROR, UNKNOWN",
    "severity": "one of: LOW, MEDIUM, HIGH, CRITICAL",
    "business_impact": "one sentence describing the business impact",
    "estimated_fix_time": "estimated time to fix e.g. 15 minutes, 1 hour, 4 hours"
}}
"""
        response = ask_claude(
            prompt=prompt,
            system="You are a senior data reliability engineer. Always respond with valid JSON only. No markdown, no explanation, just the JSON object."
        )

        # Parse Claude's JSON response into a Python dictionary
        try:
            classification = json.loads(response)
        except json.JSONDecodeError:
            # If Claude didn't return clean JSON, use a fallback
            classification = {
                "failure_type": "UNKNOWN",
                "severity": "MEDIUM",
                "business_impact": "Unable to classify automatically",
                "estimated_fix_time": "Unknown"
            }

        # Merge the classification into the pipeline data
        pipeline["classification"] = classification

        print(f"      Type: {classification['failure_type']} | Severity: {classification['severity']}")
        classified.append(pipeline)

    return {
        **state,
        "failed_pipelines": classified,
        "status": "failures_classified"
    }