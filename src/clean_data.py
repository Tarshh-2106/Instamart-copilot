import os
import pandas as pd

RAW = "data/raw"
CLEAN = "data/clean"


def clean_data():
    os.makedirs(CLEAN, exist_ok=True)
    customers = pd.read_csv(os.path.join(RAW, "customers.csv"), keep_default_na=False)
    products = pd.read_csv(os.path.join(RAW, "products.csv"), keep_default_na=False)
    orders = pd.read_csv(os.path.join(RAW, "orders.csv"), keep_default_na=False)

    customers["city"] = customers["city"].str.strip().str.title()
    customers["gender"] = customers["gender"].str.strip().str.lower().map(
        {"m": "male", "male": "male", "f": "female", "female": "female"}
    ).fillna("unknown")
    customers["age"] = pd.to_numeric(customers["age"], errors="coerce")
    customers.loc[~customers["age"].between(10, 100), "age"] = pd.NA
    customers["age"] = customers["age"].fillna(
        customers.groupby("city")["age"].transform("median")
    )
    customers["signup_date"] = pd.to_datetime(
        customers["signup_date"], errors="coerce"
    )

    products["price_inr"] = pd.to_numeric(products["price_inr"], errors="raise")

    orders["order_ts"] = pd.to_datetime(orders["order_ts"], errors="coerce")
    orders = orders.drop_duplicates()
    orders = orders.sort_values(["order_ts", "order_id"], kind="stable")
    orders = orders.drop_duplicates(subset=["order_id"], keep="last").copy()
    orders["order_amount"] = pd.to_numeric(orders["order_amount"], errors="coerce")
    orders["quantity"] = pd.to_numeric(orders["quantity"], errors="raise")
    orders["discount_pct"] = pd.to_numeric(orders["discount_pct"], errors="raise")
    prices = products.set_index("product_id")["price_inr"]
    missing_amount = orders["order_amount"].isna()
    calculated_amount = (
        orders["product_id"].map(prices)
        * orders["quantity"]
        * (1 - orders["discount_pct"] / 100)
    ).round(2)
    orders.loc[missing_amount, "order_amount"] = calculated_amount[missing_amount]

    orders["delivery_minutes"] = pd.to_numeric(
        orders["delivery_minutes"], errors="coerce"
    )
    orders.loc[orders["delivery_minutes"] < 0, "delivery_minutes"] = pd.NA
    category_by_product = products.set_index("product_id")["category"]
    orders["product_category"] = orders["product_id"].map(category_by_product)
    completed = orders["status"].eq("completed")
    orders.loc[completed, "delivery_minutes"] = orders.loc[completed, "delivery_minutes"].fillna(
        orders.loc[completed].groupby("product_category")["delivery_minutes"].transform("median")
    )
    orders = orders.drop(columns="product_category")

    frames = {
        "customers": customers,
        "products": products,
        "orders": orders,
    }
    for name, frame in frames.items():
        if name == "customers":
            frame["signup_date"] = frame["signup_date"].dt.strftime("%Y-%m-%d")
        if name == "orders":
            frame["order_ts"] = frame["order_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
        frame.to_csv(os.path.join(CLEAN, f"{name}.csv"), index=False)
        print(f"{name}.csv: {len(frame)} rows saved")

    for name in ("tickets", "policy_eval", "agent_scenarios"):
        source = os.path.join(RAW, f"{name}.csv")
        if os.path.exists(source):
            pd.read_csv(source, keep_default_na=False).to_csv(
                os.path.join(CLEAN, f"{name}.csv"), index=False
            )

    print("\nData cleaning completed.")


if __name__ == "__main__":
    clean_data()
