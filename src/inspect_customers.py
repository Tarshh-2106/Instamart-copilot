
import pandas as pd

d = pd.read_csv("data/raw/customers.csv")

print("First 5 rows:")
print(d.head())

print("\nColumn names:")
print(d.columns.tolist())

print("\nData types:")
print(d.dtypes)

print("\nMissing values:")
print(d.isnull().sum())
