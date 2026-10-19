
import os
import sys
import json
import time
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mock_llm
from redact_pii import redact

src = "data/clean/tickets.csv"
dst = "data/clean/classified_tickets_budget.csv"

cats = {"billing", "technical", "delivery", "fraud"}
budget = 100
prompt = "CLASSIFY the customer support ticket. Return only JSON with category and reason. Allowed categories: billing, technical, delivery, fraud."

d = pd.read_csv(src)
out = []
total_tokens = 0
success = 0
fallbacks = 0
skipped = 0
retries = 0

for _, r in d.iterrows():
    text = redact(r["text"] if pd.notna(r["text"]) else "")
    category = "technical"
    reason = "fallback"
    used = 0
    status = "fallback"

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": text}
    ]

    estimated = sum(
        mock_llm.est_tokens(m["content"])
        for m in messages
    )

    if not text.strip():
        reason = "Fallback: empty text"
    elif estimated > budget:
        reason = "Fallback: estimated prompt exceeds budget"
        skipped += 1
    else:
        for attempt in range(3):
            try:
                res = mock_llm.chat(messages)
                content = res.choices[0].message.content
                used = res.usage.total_tokens

                if used > budget:
                    reason = "Fallback: total token budget exceeded"
                    break

                try:
                    ans = json.loads(content)
                    c = ans.get("category")

                    if c in cats:
                        category = c
                        reason = str(ans.get("reason", ""))
                        status = "success"
                    else:
                        reason = "Fallback: invalid category"
                    break
                except (json.JSONDecodeError, TypeError):
                    reason = "Fallback: invalid JSON"
                    break

            except mock_llm.TransientLLMError:
                retries += 1
                if attempt < 2:
                    time.sleep(0.2)
                else:
                    reason = "Fallback: retry limit reached"

    total_tokens += used

    if status == "success":
        success += 1
    else:
        fallbacks += 1

    out.append({
        "ticket_id": r["ticket_id"],
        "customer_id": r["customer_id"],
        "category": category,
        "reason": reason,
        "status": status,
        "tokens": used,
        "estimated_prompt_tokens": estimated
    })

os.makedirs("data/clean", exist_ok=True)
pd.DataFrame(out).to_csv(dst, index=False)

print("Tickets processed:", len(out))
print("Successful classifications:", success)
print("Fallbacks:", fallbacks)
print("Skipped for estimated prompt budget:", skipped)
print("Retries:", retries)
print("Total recorded tokens:", total_tokens)
print("Output saved:", dst)
