
import pandas as pd

d = pd.read_csv("data/clean/customers.csv")

print("City values:")
print(sorted(d["city"].dropna().unique()))

print("\nGender values:")
print(d["gender"].value_counts(dropna=False))

print("\nSignup date type:")
print(d["signup_date"].dtype)

print("\nMissing values:")
print(d.isnull().sum())
