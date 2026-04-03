import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

def train_model():
    print("Loading processed_orders.csv...")
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "processed_orders.csv")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df):,} orders")

    # Features > for model learning
    FEATURES = [
        "cart_size",
        "reorder_rate",
        "unique_departments",
        "order_hour_anomaly",
        "is_first_order",
        "days_since_prior_order",
        "user_total_orders",
        "user_avg_reorder",
        "user_avg_cart",
        "cart_deviation",      # how different THIS order is vs user's norm
        "reorder_deviation",   # drop in reorder rate vs user's norm
        "days_deviation"       # gap change vs user's norm
    ]

    X = df[FEATURES].copy()
    print(f"Training on {len(X):,} orders, {len(FEATURES)} features")

    # STEP 2: Scale features (standardization as Isolation Forest is sensitive to scaling)
    print("Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # STEP 3: Train Isolation Forest ───────────────────────────────────
    print("Training Isolation Forest (unsupervised)...")
    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        max_samples="auto",
        random_state=42,
        n_jobs=-1        # use all CPU cores on your M2
    )
    model.fit(X_scaled)
    print("Training complete.")

    # STEP 4: Score every order ─────────────────────────────────────────
    # decision_function returns negative scores — more negative = more anomalous
    # We flip and normalise to get 0→1 where 1 = most anomalous
    print("Scoring all orders...")
    raw_scores = model.decision_function(X_scaled)
    anomaly_scores = 1 - (
        (raw_scores - raw_scores.min()) /
        (raw_scores.max() - raw_scores.min())
    )
    df["anomaly_score"] = anomaly_scores

    # STEP 5: Map score to severity ────────────────────────────────────
    # Thresholds come from the score distribution >data drivern
    p95 = np.percentile(anomaly_scores, 95)  # top 5%  = CRITICAL
    p80 = np.percentile(anomaly_scores, 80)  # top 20% = HIGH
    p60 = np.percentile(anomaly_scores, 60)  # top 40% = MEDIUM

    def score_to_severity(score):
        if score >= p95:
            return "CRITICAL"
        elif score >= p80:
            return "HIGH"
        elif score >= p60:
            return "MEDIUM"
        else:
            return "LOW"

    df["severity"] = df["anomaly_score"].apply(score_to_severity)

    # STEP 6: Show results ──────────────────────────────────────────────
    print(f"\nAnomaly score range: {anomaly_scores.min():.3f} → {anomaly_scores.max():.3f}")
    print(f"\nThresholds (data-driven from score distribution):")
    print(f"   CRITICAL : score >= {p95:.3f}  (top 5%)")
    print(f"   HIGH     : score >= {p80:.3f}  (top 20%)")
    print(f"   MEDIUM   : score >= {p60:.3f}  (top 40%)")
    print(f"   LOW      : score <  {p60:.3f}  (bottom 60%)")
    print(f"\nSeverity distribution:")
    print(df["severity"].value_counts())

    print(f"\nTop 5 most anomalous orders:")
    top = df.nlargest(5, "anomaly_score")[
        ["order_id", "anomaly_score", "severity",
         "cart_size", "reorder_rate", "cart_deviation"]]
    print(top.to_string(index=False))

    # STEP 7: Save model, scaler, scored data ───────────────────────────
    models_dir = os.path.dirname(__file__)
    joblib.dump(model,  os.path.join(models_dir, "severity_model.pkl"))
    joblib.dump(scaler, os.path.join(models_dir, "severity_scaler.pkl"))

    # Save scored data for agent queries at runtime
    scored_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "scored_orders.csv")
    df.to_csv(scored_path, index=False)

    print(f"\nModel  saved → models/severity_model.pkl")
    print(f"Scaler saved → models/severity_scaler.pkl")
    print(f"Scored data  → data/scored_orders.csv")
    print("\nDone!")

if __name__ == "__main__":
    train_model()