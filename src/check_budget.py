
import pandas as pd

d = pd.read_csv("data/clean/classified_tickets_budget.csv")

print("Columns:")
print(d.columns.tolist())

print("\nEstimated prompt tokens:")
print("Minimum:", d["estimated_prompt_tokens"].min())
print("Maximum:", d["estimated_prompt_tokens"].max())
print("Average:", round(d["estimated_prompt_tokens"].mean(), 2))

print("\nInputs over budget:")
print((d["estimated_prompt_tokens"] > 100).sum())

print("\nFallback reasons:")
print(d.loc[d["status"] != "success", "reason"].value_counts())

print("\nSuccessful classifications over 100 recorded tokens:")
print(((d["status"] == "success") & (d["tokens"] > 100)).sum())
