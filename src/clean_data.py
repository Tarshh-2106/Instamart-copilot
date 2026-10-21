
import os
import pandas as pd

src = "data/raw"
dst = "data/clean"

os.makedirs(dst, exist_ok=True)

p = pd.read_csv(os.path.join(src, "products.csv"))
prices = p.set_index("product_id")["price_inr"]

for f in os.listdir(src):
    if not f.endswith(".csv"):
        continue

    d = pd.read_csv(os.path.join(src, f))

    for c in d.select_dtypes(include=["object", "str"]).columns:
        d[c] = d[c].str.strip()

    if f == "customers.csv":
        d["city"] = d["city"].str.title()
        d["signup_date"] = pd.to_datetime(
            d["signup_date"], errors="coerce"
        ).dt.strftime("%Y-%m-%d")
        d["gender"] = d["gender"].str.upper().replace({
            "M": "MALE",
            "F": "FEMALE"
        })

    if f == "orders.csv":
        d["order_ts"] = pd.to_datetime(
            d["order_ts"], errors="coerce"
        )
        d["order_amount"] = pd.to_numeric(
            d["order_amount"], errors="coerce"
        )
        d["delivery_minutes"] = pd.to_numeric(
            d["delivery_minutes"], errors="coerce"
        )
        d["quantity"] = pd.to_numeric(
            d["quantity"], errors="coerce"
        )
        d["discount_pct"] = pd.to_numeric(
            d["discount_pct"], errors="coerce"
        )

        d.loc[d["delivery_minutes"] < 0, "delivery_minutes"] = float("nan")

        mask = d["status"].eq("completed") & d["order_amount"].isna()
        price = d["product_id"].map(prices)
        amount = price * d["quantity"] * (1 - d["discount_pct"] / 100)
        d.loc[mask, "order_amount"] = amount.loc[mask].round(2)

        d = d.drop_duplicates()
        d = d[d["status"].isin(["completed", "cancelled"])].copy()
        d = d.sort_values("order_ts")
        d = d.drop_duplicates(subset=["order_id"], keep="last")

    d.to_csv(os.path.join(dst, f), index=False)
    print(f"{f}: {len(d)} rows saved")

print("\nBasic cleaning completed.")
