import os
import pandas as pd

os.makedirs("outputs", exist_ok=True)
rows = ["# Raw data audit"]
for name in ("customers", "orders", "tickets"):
    frame = pd.read_csv(
        f"data/raw/{name}.csv",
        keep_default_na=False if name == "tickets" else True
    )
    rows.append(f"\n## {name}.csv — shape {frame.shape}")
    rows.append("\nColumn | dtype | missing count | missing percent\n---|---|---:|---:")
    missing = frame.replace("", pd.NA).isna().sum()
    for column in frame.columns:
        rows.append(
            f"{column} | {frame[column].dtype} | {int(missing[column])} | "
            f"{100 * missing[column] / len(frame):.2f}%"
        )

orders = pd.read_csv("data/raw/orders.csv", keep_default_na=False)
customers = pd.read_csv("data/raw/customers.csv", keep_default_na=False)
audit = {
    "raw order rows": len(orders),
    "exact duplicate order rows": int(orders.duplicated().sum()),
    "pending rows": int(orders["status"].eq("pending").sum()),
    "distinct order IDs": int(orders["order_id"].nunique()),
    "non-numeric amounts": int(pd.to_numeric(orders["order_amount"], errors="coerce").isna().sum()),
    "negative delivery times": int(pd.to_numeric(orders["delivery_minutes"], errors="coerce").lt(0).sum()),
    "blank delivery times": int(orders["delivery_minutes"].eq("").sum()),
    "blank ages": int(customers["age"].eq("").sum()),
    "ages outside 10–100": int(
        (~pd.to_numeric(customers["age"], errors="coerce").dropna().between(10, 100)).sum()
    ),
    "distinct raw city spellings": int(customers["city"].nunique()),
    "distinct nonblank gender spellings": int(customers.loc[customers["gender"].ne(""), "gender"].nunique()),
    "blank genders": int(customers["gender"].eq("").sum()),
}
rows.extend(["\n## Required raw-data checkpoints", "\nMetric | Count\n---|---:"])
rows.extend(f"{metric} | {value}" for metric, value in audit.items())
with open("outputs/raw_data_audit.md", "w", encoding="utf-8") as report:
    report.write("\n".join(rows) + "\n")
print("Saved outputs/raw_data_audit.md")
