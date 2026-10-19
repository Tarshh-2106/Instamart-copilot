
import pandas as pd

d = pd.read_csv("data/raw/orders.csv", dtype={"order_amount": "str"})

a = d["order_amount"]
n = pd.to_numeric(a, errors="coerce")

bad = a.notna() & n.isna()

print("Originally missing amounts:", a.isna().sum())
print("Non-numeric amount values:", bad.sum())

print("\nExamples of non-numeric values:")
print(a[bad].value_counts().head(20))

print("\nAffected order records:")
print(d.loc[bad, ["order_id", "status", "order_amount"]].head(15).to_string(index=False))
