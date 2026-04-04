import pandas as pd
import numpy as np
import os
from datetime import datetime

def get_pipeline_failures():
    """
    Generates real pipeline runs from scored_orders.csv.
    Orders are split into time-based batches.
    Each batch IS a pipeline run.
    Failures are determined by real anomaly scores — not hardcoded.
    """
    scored_path = os.path.join(
        os.path.dirname(__file__), "scored_orders.csv")

    if not os.path.exists(scored_path):
        print("   ⚠️  scored_orders.csv not found")
        return []

    df = pd.read_csv(scored_path)

    # ── Split orders into time-based pipeline run batches ─────────────────
    # Each batch represents one pipeline execution window
    bins = [0, 5, 11, 17, 23]
    labels = [
        "instacart_earlymorning_batch",    # 12am - 5am
        "instacart_morning_batch",          # 6am - 11am
        "instacart_afternoon_batch",        # 12pm - 5pm
        "instacart_evening_batch"           # 6pm - 11pm
      ]

    df["pipeline_run"] = pd.cut(
        df["order_hour_of_day"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    # ── Evaluate each batch as a pipeline run ─────────────────────────────
    FAILURE_THRESHOLD = 0.35  # avg anomaly score above this = pipeline failed

    pipeline_runs = []
    for label in labels:
        batch = df[df["pipeline_run"] == label]
        if batch.empty:
            continue

        avg_score     = round(batch["anomaly_score"].mean(), 3)
        critical_ct   = len(batch[batch["severity"] == "CRITICAL"])
        high_ct       = len(batch[batch["severity"] == "HIGH"])
        total_ct      = len(batch)
        critical_rate = round(critical_ct / total_ct * 100, 2)
        avg_cart      = round(batch["cart_size"].mean(), 1)
        avg_reorder   = round(batch["reorder_rate"].mean(), 3)
        top_score     = round(batch["anomaly_score"].max(), 3)
        top_order     = int(batch.loc[
            batch["anomaly_score"].idxmax(), "order_id"])

        status = "FAILED" if avg_score >= FAILURE_THRESHOLD else "SUCCESS"

        run = {
            "pipeline_id": f"PL_{labels.index(label)+1:03d}",
            "name":        label,
            "status":      status,
            "database":    "Instacart_Orders_DB",
            "last_run":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_orders": total_ct,
            "avg_anomaly_score": avg_score,
            "real_stats": {
                "total_orders":    total_ct,
                "critical_orders": critical_ct,
                "high_orders":     high_ct,
                "critical_rate":   critical_rate,
                "avg_cart_size":   avg_cart,
                "avg_reorder":     avg_reorder,
                "top_score":       top_score,
                "top_order_id":    top_order
            }
        }

        # Build real error message from data
        if status == "FAILED":
            run["error"] = (
                f"Batch anomaly threshold breached: avg score {avg_score} "
                f"exceeds limit of {FAILURE_THRESHOLD}. "
                f"{critical_ct:,} CRITICAL orders ({critical_rate}%) "
                f"in {total_ct:,} total orders processed. "
                f"Top anomalous order_id {top_order} scored {top_score}. "
                f"Avg cart size: {avg_cart} items, "
                f"avg reorder rate: {avg_reorder}."
            )
        else:
            run["error"] = None

        pipeline_runs.append(run)

    # Return only failed pipelines
    failed = [r for r in pipeline_runs if r["status"] == "FAILED"]

    print(f"   Pipeline runs evaluated: {len(pipeline_runs)}")
    print(f"   Failed runs: {len(failed)}")

    return failed


# ── Dependency map — Instacart batch processing architecture ──────────────────
DEPENDENCY_MAP = {
    "instacart_earlymorning_batch": {
        "upstream_sources": [
            "Instacart_App_Event_Stream",
            "Instacart_API_Gateway",
            "Kafka_Order_Topic"
        ],
        "downstream_dependents": [
            "instacart_fraud_detection_pipeline",
            "instacart_payment_processing_pipeline",
            "instacart_shopper_assignment_pipeline"
        ],
        "shared_infrastructure": [
            "Instacart_Orders_DB",
            "Kafka_Event_Bus",
            "Snowflake_Staging"
        ]
    },
    "instacart_morning_batch": {
        "upstream_sources": [
            "Instacart_App_Event_Stream",
            "Instacart_Partner_Store_API",
            "Instacart_Inventory_Feed"
        ],
        "downstream_dependents": [
            "instacart_inventory_allocation_pipeline",
            "instacart_delivery_routing_pipeline",
            "instacart_analytics_reporting_pipeline"
        ],
        "shared_infrastructure": [
            "Instacart_Orders_DB",
            "Instacart_Inventory_DB",
            "Snowflake_Data_Warehouse"
        ]
    },
    "instacart_afternoon_batch": {
        "upstream_sources": [
            "Instacart_App_Event_Stream",
            "Instacart_Promotions_Engine",
            "Instacart_Shopper_App"
        ],
        "downstream_dependents": [
            "instacart_revenue_reporting_pipeline",
            "instacart_personalisation_engine",
            "instacart_customer_retention_pipeline"
        ],
        "shared_infrastructure": [
            "Instacart_Orders_DB",
            "Instacart_Promotions_DB",
            "ChromaDB_Vector_Store"
        ]
    },
    "instacart_evening_batch": {
        "upstream_sources": [
            "Instacart_App_Event_Stream",
            "Instacart_Express_Membership_Service",
            "Instacart_Ratings_API"
        ],
        "downstream_dependents": [
            "instacart_churn_prediction_model",
            "instacart_marketing_campaign_pipeline",
            "instacart_executive_dashboard"
        ],
        "shared_infrastructure": [
            "Instacart_Orders_DB",
            "ML_Model_Registry",
            "Instacart_Users_DB"
        ]
    }
}

# ── Public API ────────────────────────────────────────────────────────────────
PIPELINE_FAILURES = get_pipeline_failures()

# Alias for files that still reference the old name
PIPELINE_FAILURES = PIPELINE_FAILURES