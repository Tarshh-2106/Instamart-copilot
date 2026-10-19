
import pandas as pd

d = pd.read_csv("data/clean/classified_tickets.csv")
t = pd.read_csv("data/clean/tickets.csv")

print("Total records:", len(d))
print("Duplicate ticket IDs:", d["ticket_id"].duplicated().sum())
print("\nPrediction counts:")
print(d["category"].value_counts(dropna=False))

print("\nStatus counts:")
print(d["status"].value_counts(dropna=False))

print("\nFallback reasons:")
print(
    d.loc[d["status"] != "success", "reason"]
    .value_counts(dropna=False)
)

print("\nToken usage:")
print("Total:", d["tokens"].sum())
print("Average per ticket:", round(d["tokens"].mean(), 2))
print("Maximum per ticket:", d["tokens"].max())

m = d.merge(
    t[["ticket_id", "true_category"]],
    on="ticket_id",
    how="left"
)

ok = m["status"] == "success"

print("\nSuccessful predictions:", ok.sum())

if ok.any():
    print(
        "Accuracy on successful predictions:",
        round(
            (m.loc[ok, "category"] == m.loc[ok, "true_category"]).mean()
            * 100,
            2
        ),
        "%"
    )
