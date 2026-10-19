
import pandas as pd

d = pd.read_csv("data/clean/tickets.csv")

print("Total tickets:", len(d))
print("\nMissing values:")
print(d.isnull().sum())

print("\nTicket categories:")
print(d["true_category"].value_counts(dropna=False))

print("\nMissing ticket text:", d["text"].isna().sum())
print("Missing order IDs:", d["order_id"].isna().sum())
print("Duplicate ticket IDs:", d["ticket_id"].duplicated().sum())
print("Duplicate customer IDs:", d["customer_id"].duplicated().sum())
