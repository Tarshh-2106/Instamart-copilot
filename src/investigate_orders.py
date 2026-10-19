
import pandas as pd

d = pd.read_csv("data/clean/orders.csv")

print("Sample order amounts:")
print(d["order_amount"].dropna().head(20).to_list())

print("\nOrder amount data type:")
print(d["order_amount"].dtype)

print("\nExample repeated order IDs:")
ids = d.loc[d["order_id"].duplicated(keep=False), "order_id"].unique()

if len(ids):
    print(d[d["order_id"] == ids[0]].to_string(index=False))

print("\nExample exact duplicate records:")
print(d[d.duplicated(keep=False)].head(10).to_string(index=False))

print("\nMissing order amounts by status:")
print(
    d[d["order_amount"].isna()]["status"]
    .value_counts(dropna=False)
)
