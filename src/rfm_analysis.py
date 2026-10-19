import os
import pandas as pd

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = os.path.join(base, "data", "clean")
out = os.path.join(base, "outputs")

os.makedirs(out, exist_ok=True)

orders = pd.read_csv(os.path.join(data, "orders.csv"))
orders["order_ts"] = pd.to_datetime(orders["order_ts"], errors="coerce")
orders["order_amount"] = pd.to_numeric(orders["order_amount"], errors="coerce")

orders = orders[orders["status"].eq("completed")].copy()
orders = orders.dropna(subset=["customer_id", "order_ts", "order_amount"])

ref_date = orders["order_ts"].max().normalize() + pd.Timedelta(days=1)

rfm = orders.groupby("customer_id").agg(
    last_order=("order_ts", "max"),
    frequency=("order_id", "nunique"),
    monetary=("order_amount", "sum")
)

rfm["recency"] = (ref_date - rfm["last_order"]).dt.days
rfm = rfm[["recency", "frequency", "monetary"]].reset_index()

path = os.path.join(out, "rfm_features.csv")
rfm.to_csv(path, index=False)

print("RFM features created:", len(rfm), "customers")
print("\nSummary:")
print(rfm[["recency", "frequency", "monetary"]].describe().round(2))
print("\nSample:")
print(rfm.head(10).to_string(index=False))
print("\nSaved to:", path)