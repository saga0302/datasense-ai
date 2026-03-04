DEPENDENCY_MAP = {
        "sales_daily_etl": {
            "upstream_sources": ["S3 raw sales bucket", "Salesforce CRM API"],
            "downstream_dependents": ["finance_reporting_etl", "executive_dashboard", "sales_forecast_model"],
            "shared_infrastructure": ["Snowflake warehouse XL", "Azure Data Factory"]
        },
        "customer_data_warehouse": {
            "upstream_sources": ["CRM database", "support_tickets_etl", "web_events_stream"],
            "downstream_dependents": ["marketing_attribution", "churn_prediction_model", "customer_360_report"],
            "shared_infrastructure": ["Snowflake warehouse XL", "dbt transformations"]
        },
        "finance_reporting_etl": {
            "upstream_sources": ["sales_daily_etl", "accounts_payable_db", "S3 finance bucket"],
            "downstream_dependents": ["board_reporting_dashboard", "regulatory_compliance_export", "CFO_weekly_report"],
            "shared_infrastructure": ["Azure SQL", "S3 finance bucket"]
        }
    }

def investigate_upstream(state: dict) -> dict:
    """
    Node 3: For each failed pipeline, checks what upstream dependencies
    are affected. Simulates what a real SQL dependency query would return.
    """
    print("\n Node 3: Investigating upstream dependencies...")

    # Mock dependency map — in production this would be a SQL query
    # showing which pipelines feed into which other pipelines

    failed_pipelines = state.get("failed_pipelines", [])
    total_downstream_affected = set()

    for pipeline in failed_pipelines:
        name = pipeline["name"]
        deps = DEPENDENCY_MAP.get(name, {
            "upstream_sources": ["Unknown"],
            "downstream_dependents": [],
            "shared_infrastructure": []
        })

        pipeline["dependencies"] = deps

        # Track all unique downstream systems affected
        for d in deps["downstream_dependents"]:
            total_downstream_affected.add(d)

        print(f"   → {name}")
        print(f"      Upstream sources    : {', '.join(deps['upstream_sources'])}")
        print(f"      Downstream affected : {', '.join(deps['downstream_dependents'])}")

    print(f"\n   Total unique downstream systems at risk: {len(total_downstream_affected)}")

    return {
        **state,
        "failed_pipelines": failed_pipelines,
        "total_downstream_affected": list(total_downstream_affected),
        "status": "investigation_complete"
    }