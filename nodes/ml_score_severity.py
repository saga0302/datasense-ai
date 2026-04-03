import pandas as pd
import numpy as np
import joblib
import os

def ml_score_severity(state: dict) -> dict:
    """
    Node 2.5: Loads the trained Isolation Forest model and scores
    each failed pipeline using real Instacart order patterns.
    Adds anomaly_score, severity_label, and top_features to state.
    """
    print("Node 2.5: Scoring anomalies with Isolation Forest...")

    failed_pipelines = state.get("failed_pipelines", [])

    # ── Load model and scaler ─────────────────────────────────────────────
    base = os.path.dirname(__file__)
    model_path  = os.path.join(base, "..", "models", "severity_model.pkl")
    scaler_path = os.path.join(base, "..", "models", "severity_scaler.pkl")
    data_path   = os.path.join(base, "..", "data",   "scored_orders.csv")

    if not os.path.exists(model_path):
        print(" Model not found — skipping ML scoring")
        return {**state, "status": "ml_score_skipped"}

    model  = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    print("  Model and scaler loaded")

    if not os.path.exists(data_path):
        print(" scored_orders.csv not found — skipping ML scoring")
        return {**state, "status": "ml_score_skipped"}

    scored_df = pd.read_csv(data_path)
    print(f" {len(scored_df):,} scored orders available")

    # ── Feature columns — must match training exactly 
    FEATURES = [
        "cart_size", "reorder_rate", "unique_departments",
        "order_hour_anomaly", "is_first_order",
        "days_since_prior_order", "user_total_orders",
        "user_avg_reorder", "user_avg_cart",
        "cart_deviation", "reorder_deviation", "days_deviation"
    ]

    FEATURE_LABELS = {
        "cart_size":              "unusually large cart",
        "reorder_rate":           "low reorder rate",
        "unique_departments":     "spans many departments",
        "order_hour_anomaly":     "anomalous order hour",
        "is_first_order":         "first-time order risk",
        "days_since_prior_order": "long gap since last order",
        "user_total_orders":      "low-retention user",
        "user_avg_reorder":       "low personal reorder baseline",
        "user_avg_cart":          "personal cart norm deviation",
        "cart_deviation":         "cart far from user baseline",
        "reorder_deviation":      "sharp reorder behaviour drop",
        "days_deviation":         "unusual gap vs personal pattern"
    }

    # ── Score each failed pipeline ────────────────────────────────────────
    for pipeline in failed_pipelines:
        print(f"   → Scoring: {pipeline['name']}...")

        # Pull the top 200 most anomalous orders as representative sample
        # In production this would filter by pipeline ID and time window
        sample = scored_df.nlargest(200, "anomaly_score").copy()

        if sample.empty:
            pipeline["ml_score"] = {
                "anomaly_score":   0.5,
                "severity_label":  "MEDIUM",
                "top_features":    "insufficient data",
                "orders_analysed": 0
            }
            continue

        # Scale using the SAME scaler from training — critical
        X_sample = sample[FEATURES].fillna(0)
        X_scaled = scaler.transform(X_sample)

        # Get raw scores from model
        raw_scores = model.decision_function(X_scaled)

        # Normalise to 0→1 using training distribution bounds
        raw_min, raw_max = -0.5, 0.5
        norm = 1 - ((raw_scores - raw_min) / (raw_max - raw_min))
        norm = np.clip(norm, 0, 1)
        anomaly_score = float(np.mean(norm))

        # Map to severity using same thresholds from training
        if   anomaly_score >= 0.488: severity_label = "CRITICAL"
        elif anomaly_score >= 0.279: severity_label = "HIGH"
        elif anomaly_score >= 0.181: severity_label = "MEDIUM"
        else:                        severity_label = "LOW"

        # Find top 3 driving features
        col_means = X_scaled.mean(axis=0)
        feature_deviations = {
            feat: float(abs(X_scaled[:, i].mean() - col_means[i]))
            for i, feat in enumerate(FEATURES)
        }
        top_3 = sorted(
            feature_deviations.items(),
            key=lambda x: x[1], reverse=True
        )[:3]

        top_features_str = ", ".join(
            FEATURE_LABELS[f] for f, _ in top_3
        )

        pipeline["ml_score"] = {
            "anomaly_score":   round(anomaly_score, 3),
            "severity_label":  severity_label,
            "top_features":    top_features_str,
            "orders_analysed": len(sample)
        }

        print(f"      Score: {anomaly_score:.3f} | "
              f"Severity: {severity_label} | "
              f"Top signal: {top_3[0][0]}")

    print("\n ML scoring complete")

    return {
        **state,
        "failed_pipelines": failed_pipelines,
        "status": "ml_scored"
    }