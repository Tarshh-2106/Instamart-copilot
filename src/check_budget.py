
import pandas as pd

d = pd.read_csv("outputs/triage_budget_demo.csv")

print("Columns:")
print(d.columns.tolist())

classified = d["status"].isin({"classified_json", "classified_text"})
print("\nRecorded tokens:")
print("Total:", int(d["tokens"].sum()))
print("Average per ticket:", round(d["tokens"].mean(), 2))

print("\nBudget-exhausted tickets:")
print(d["status"].eq("budget_exhausted").sum())

print("\nFallback reasons:")
print(d.loc[~classified, "reason"].value_counts())

print("\nClassified tickets:")
print(int(classified.sum()))
