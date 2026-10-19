
import pandas as pd

d = pd.read_csv("data/raw/policy_eval.csv")

print("First 5 rows:")
print(d.head().to_string())

print("\nColumn names:")
print(d.columns.tolist())

print("\nData types:")
print(d.dtypes)

print("\nMissing values:")
print(d.isnull().sum())

print("\nDuplicate rows:", d.duplicated().sum())
