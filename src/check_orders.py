
import pandas as pd

d = pd.read_csv("data/clean/orders.csv")

print("Total rows:", len(d))
print("Unique order IDs:", d["order_id"].nunique())
print("Repeated order IDs:", d["order_id"].duplicated().sum())

print("\nExact duplicate rows:", d.duplicated().sum())

print("\nMissing order amounts:", d["order_amount"].isna().sum())
print("\nExamples of missing amounts:")
print(d.loc[d["order_amount"].isna()].head().to_string(index=False))

print("\nOrder status counts:")
print(d["status"].value_counts(dropna=False))

print("\nQuantity minimum:", d["quantity"].min())
print("Discount minimum:", d["discount_pct"].min())
print("Discount maximum:", d["discount_pct"].max())
