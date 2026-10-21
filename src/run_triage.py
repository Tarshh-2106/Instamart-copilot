
import os
import sys
import json
import time
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mock_llm
from redact_pii import redact

TOKEN_BUDGET = 100000
DEMO_BUDGET = 6000
CATS = {"billing", "technical", "delivery", "fraud"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def route_ticket(segment):
    s = str(segment).lower()

    if "lapsed" in s or "risk" in s:
        return "retention_team"
    if "premium" in s or "spending" in s:
        return "priority_support"
    if "frequent" in s or "recent" in s:
        return "loyal_customer_support"
    return "general_support"

def classify(d, segments, budget, few_shot, dst):
    mock_llm.reset()

    out = []
    spent = 0
    successes = 0
    fallbacks = 0
    retries = 0

    for _, r in d.iterrows():
        text = redact(r["text"] if pd.notna(r["text"]) else "")
        customer_id = str(r["customer_id"])
        segment = segments.get(customer_id, "Occasional")
        category = "technical"
        reason = ""
        status = "fallback"
        used = 0

        if not text.strip():
            reason = "empty_text"
        elif spent >= budget:
            reason = "budget_exhausted"
        else:
            prompt = (
                "CLASSIFY each customer support ticket. Return only JSON "
                "with category and reason. Allowed categories: billing, "
                "technical, delivery, fraud."
            )

            if few_shot:
                prompt += (
                    "\nEXAMPLES:\n"
                    "Unauthorized card transaction -> fraud\n"
                    "Wrong invoice amount -> billing\n"
                    "App crashes during payment -> technical\n"
                    "Late rider delivery -> delivery"
                )

            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]


            estimated = sum(
                mock_llm.est_tokens(m["content"])
                for m in messages
            )
            reserve = 40

            if spent + estimated + reserve > budget:
                reason = "budget_exhausted"
            else:
                for attempt in range(3):
                    try:
                        res = mock_llm.chat(messages)
                        content = res.choices[0].message.content
                        used = res.usage.total_tokens

                        if spent + used > budget:
                            spent += used
                            reason = "budget_exhausted"
                            break

                        spent += used

                        try:
                            ans = json.loads(content or "")
                            c = ans.get("category")

                            if c in CATS:
                                category = c
                                reason = str(ans.get("reason", ""))
                                status = "success"
                            else:
                                reason = "invalid_category"
                        except (json.JSONDecodeError, TypeError, AttributeError):
                            reason = "invalid_json"

                        break

                    except mock_llm.TransientLLMError:
                        retries += 1
                        if attempt < 2:
                            time.sleep(0.2)
                        else:
                            reason = "retry_limit_reached"

        if status == "success":
            successes += 1
        else:
            fallbacks += 1

        out.append({
            "ticket_id": r["ticket_id"],
            "customer_id": customer_id,
            "true_category": r["true_category"],
            "category": category,
            "reason": reason,
            "status": status,
            "customer_segment": segment,
            "assigned_team": route_ticket(segment),
            "tokens": used,
            "cumulative_tokens": spent
        })

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    pd.DataFrame(out).to_csv(dst, index=False)

    print("\nOutput:", os.path.relpath(dst, ROOT))
    print("Tickets processed:", len(out))
    print("Successful classifications:", successes)
    print("Fallbacks:", fallbacks)
    print("Retries:", retries)
    print("Total recorded tokens:", spent)
    print("Fallback reasons:")
    print(pd.Series([x["reason"] for x in out if x["status"] != "success"]).value_counts().to_string())

    return pd.DataFrame(out)

def main():
    os.chdir(ROOT)

    tickets = pd.read_csv("data/clean/tickets.csv")
    customer_data = pd.read_csv("outputs/customer_segments.csv")

    if "customer_id" not in customer_data.columns:
        raise ValueError("customer_segments.csv must contain customer_id")

    seg_col = next(
    (c for c in ["segment_name", "customer_segment", "segment"]
     if c in customer_data.columns),
    None
    )

    if seg_col is None:
        raise ValueError("Could not find the customer segment column")

    segments = dict(zip(
        customer_data["customer_id"].astype(str),
        customer_data[seg_col].astype(str)
    ))

    print("Few-shot run")
    classify(
        tickets,
        segments,
        TOKEN_BUDGET,
        True,
        "outputs/triage_results.csv"
    )

    print("\nZero-shot budget demo")
    classify(
        tickets,
        segments,
        DEMO_BUDGET,
        False,
        "outputs/triage_budget_demo.csv"
    )

if __name__ == "__main__":
    main()
