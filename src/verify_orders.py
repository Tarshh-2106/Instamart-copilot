
import pandas as pd

raw = pd.read_csv("data/raw/orders.csv", dtype={"order_amount": "str"})
clean = pd.read_csv("data/clean/orders.csv")

print("Raw rows:", len(raw))
print("Cleaned rows:", len(clean))
print("Exact duplicates removed:", len(raw) - len(clean))

print("\nRaw missing amounts:", raw["order_amount"].isna().sum())
print("Raw error amounts:", raw["order_amount"].eq("error").sum())
print("Cleaned missing amounts:", clean["order_amount"].isna().sum())

print("\nCleaned amount type:", clean["order_amount"].dtype)
print("Remaining exact duplicates:", clean.duplicated().sum())
