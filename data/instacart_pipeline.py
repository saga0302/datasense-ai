import pandas as pd
import numpy as np
import os

def run_pipeline():
    print("Starting Instacart pipeline...")

    BASE = os.path.join(os.path.dirname(__file__), "instacart")

    # STEP 1: Load tables 
    print("Loading CSVs...")
    orders = pd.read_csv(os.path.join(BASE, "orders.csv"))
    order_products = pd.read_csv(
        os.path.join(BASE, "order_products__train.csv"))
    products = pd.read_csv(os.path.join(BASE, "products.csv"))
    aisles = pd.read_csv(os.path.join(BASE, "aisles.csv"))

    print(f"Orders: {len(orders):,} rows")
    print(f"Order products: {len(order_products):,} rows")

    #STEP 2: Join product detail 
    print("Joining tables...")
    order_products = order_products.merge(
        products[["product_id", "aisle_id"]], on="product_id", how="left")
    order_products = order_products.merge(
        aisles[["aisle_id", "aisle"]], on="aisle_id", how="left")

    # STEP 3: Aggregate to one row per order 
    print("Aggregating features per order...")
    agg = order_products.groupby("order_id").agg(
        cart_size=("product_id", "count"),
        reorder_rate=("reordered", "mean"),
        unique_departments=("aisle_id", "nunique")
    ).reset_index()

    # STEP 4: Merge with orders 
    df = orders.merge(agg, on="order_id", how="inner")
    print(f"Merged dataset: {len(df):,} orders")

    # STEP 5: Efeature engineering
    print("Engineering features...")
    df["order_hour_anomaly"] = df["order_hour_of_day"].apply(
        lambda h: 1 if 1 <= h <= 5 else 0)
    df["is_first_order"] = df["order_number"].apply(
        lambda n: 1 if n == 1 else 0)
    df["days_since_prior_order"] = df["days_since_prior_order"].fillna(0)

    # STEP 6: User-level behavioural base
    print("Building user behavioural baselines...")
    user_stats = df.groupby("user_id").agg(
        user_total_orders=("order_number", "max"),
        user_avg_reorder=("reorder_rate", "mean"),
        user_avg_cart=("cart_size", "mean"),
        user_std_cart=("cart_size", "std"),
        user_avg_days=("days_since_prior_order", "mean")
    ).reset_index()

    df = df.merge(user_stats, on="user_id", how="left")
    df["user_std_cart"] = df["user_std_cart"].fillna(0)

    # Deviation from personal baseline 
    df["cart_deviation"] = (
        (df["cart_size"] - df["user_avg_cart"]) /
        (df["user_std_cart"] + 1)  # +1 to avoid division by zero
    )
    df["reorder_deviation"] = (
        df["user_avg_reorder"] - df["reorder_rate"]
    )
    df["days_deviation"] = (
        df["days_since_prior_order"] - df["user_avg_days"]
    )

    #STEP 7: Select final feature columns 
    final_cols = [
        "order_id", "user_id", "order_number",
        "order_hour_of_day", "days_since_prior_order",
        "cart_size", "reorder_rate", "unique_departments",
        "order_hour_anomaly", "is_first_order",
        "user_total_orders", "user_avg_reorder", "user_avg_cart",
        "cart_deviation", "reorder_deviation", "days_deviation"
    ]
    df = df[final_cols]

    # STEP 8: Save to fold
    out_path = os.path.join(
        os.path.dirname(__file__), "processed_orders.csv")
    df.to_csv(out_path, index=False)

    print(f"\nDone! {len(df):,} orders saved to processed_orders.csv")
    print(f"Features: {len(final_cols) - 2} columns (excl. order_id, user_id)")

if __name__ == "__main__":
    run_pipeline()