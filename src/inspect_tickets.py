
import pandas as pd

d = pd.read_csv("data/raw/tickets.csv", keep_default_na=False)

print("First 5 rows:")
print(d.head().to_string())

print("\nColumn names:")
print(d.columns.tolist())

print("\nData types:")
print(d.dtypes)

print("\nMissing values:")
print(d.isnull().sum())
print("\nEmpty ticket text:", d["text"].eq("").sum())

print("\nDuplicate rows:", d.duplicated().sum())
