
import pandas as pd
from redact_pii import redact

d = pd.read_csv("data/clean/tickets.csv")

print("Total tickets:", len(d))

for _, r in d.head(10).iterrows():
    text = r["text"] if pd.notna(r["text"]) else ""
    safe = redact(text)

    print("\nTicket:", r["ticket_id"])
    print("Original:", text)
    print("Redacted:", safe)

    if not safe:
        print("Status: Empty ticket text")
