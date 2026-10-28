
import pandas as pd
from redact_pii import redact

assert redact("Email user@example.com") == "Email [EMAIL]"
assert redact("Call 7766326255") == "Call [PHONE]"
assert redact("Refund ORD-123456") == "Refund [ORDER_ID]"

d = pd.read_csv("data/clean/tickets.csv", keep_default_na=False)

print("Total tickets:", len(d))

for _, r in d.head(10).iterrows():
    text = r["text"] if pd.notna(r["text"]) else ""
    safe = redact(text)

    print("\nTicket:", r["ticket_id"])
    print("Original:", text)
    print("Redacted:", safe)

    if not safe:
        print("Status: Empty ticket text")
