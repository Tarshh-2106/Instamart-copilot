
import pandas as pd

d = pd.read_csv("data/clean/tickets.csv", keep_default_na=False)

print("Total tickets:", len(d))
print("\nMissing values:")
print(d.isnull().sum())

print("\nTicket categories:")
print(d["true_category"].value_counts(dropna=False))

print("\nMissing ticket text:", d["text"].isna().sum())
print("Empty ticket text:", d["text"].eq("").sum())
print("Missing order IDs:", d["order_id"].isna().sum())
print("Blank order IDs:", d["order_id"].eq("").sum())
print("Duplicate ticket IDs:", d["ticket_id"].duplicated().sum())
print("Duplicate customer IDs:", d["customer_id"].duplicated().sum())
