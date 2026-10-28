import json
import os
import random
import re
import sys
import time
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mock_llm
from redact_pii import redact

TOKEN_BUDGET = 100000
DEMO_BUDGET = 6000
MAX_INPUT_TOKENS = 120
CATEGORIES = {"billing", "delivery", "technical", "fraud"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RNG = random.Random(42)


def route_ticket(segment, status):
    if status == "budget_exhausted":
        return "human_review"
    value = str(segment).lower()
    if "lapsed" in value or "risk" in value:
        return "retention_team"
    if "premium" in value or "spending" in value:
        return "priority_support"
    if "frequent" in value or "recent" in value:
        return "loyal_customer_support"
    return "general_support"


def parse_response(content):
    try:
        answer = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        words = set(re.findall(r"[a-z]+", (content or "").lower()))
        category = next((name for name in CATEGORIES if name in words), None)
        if category:
            return category, "classified_text", "non_json_category_match"
        return "unclassified", "fallback", "invalid_json"

    if isinstance(answer, dict) and answer.get("category") in CATEGORIES:
        return answer["category"], "classified_json", str(answer.get("reason", ""))
    return "unclassified", "fallback", "invalid_category"


def classify(tickets, segments, budget, few_shot, output_path):
    mock_llm.reset()
    spent = 0
    retries = 0
    records = []

    system = (
        "CLASSIFY each support ticket. Return JSON only in the form "
        '{"category":"billing|delivery|technical|fraud","reason":"brief reason"}. '
        "Allowed categories: billing, delivery, technical, fraud."
    )
    if few_shot:
        system += (
            "\nEXAMPLES:\n"
            "Unauthorized card transaction -> fraud\n"
            "Wrong invoice amount -> billing\n"
            "App crashes during payment -> technical\n"
            "Late rider delivery -> delivery"
        )

    for _, row in tickets.iterrows():
        text = redact(row["text"] if pd.notna(row["text"]) else "")
        customer_id = str(row["customer_id"])
        segment = segments.get(customer_id, "Occasional Customers")
        status = "fallback"
        reason = ""
        category = "unclassified"
        used = 0
        is_empty = not text.strip()

        if is_empty:
            status, reason = "skipped_empty", "empty_text"
        elif mock_llm.est_tokens(text) > MAX_INPUT_TOKENS:
            status, reason = "skipped_too_long", "input_token_limit"
        elif spent >= budget:
            status, reason = "budget_exhausted", "token_budget_exhausted"
        else:
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": text},
            ]
            prompt_tokens = sum(mock_llm.est_tokens(m["content"]) for m in messages)
            if spent + prompt_tokens + 40 > budget:
                status, reason = "budget_exhausted", "token_budget_exhausted"
            else:
                for retry in range(4):
                    try:
                        response = mock_llm.chat(messages)
                        used = response.usage.total_tokens
                        spent += used
                        if spent > budget:
                            status, reason = "budget_exhausted", "token_budget_exhausted"
                            break
                        category, status, reason = parse_response(
                            response.choices[0].message.content
                        )
                        break
                    except mock_llm.TransientLLMError:
                        retries += 1
                        if retry == 3:
                            status, reason = "fallback", "retry_limit_reached"
                        else:
                            time.sleep(RNG.uniform(0, 0.05 * (2 ** retry)))

        records.append({
            "ticket_id": row["ticket_id"],
            "customer_id": customer_id,
            "true_category": row["true_category"],
            "category": category,
            "reason": reason,
            "status": status,
            "customer_segment": segment,
            "assigned_team": route_ticket(segment, status),
            "tokens": used,
            "cumulative_tokens": spent,
        })

    result = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.to_csv(output_path, index=False)
    classified = result["status"].isin({"classified_json", "classified_text"})
    accuracy = (
        (result.loc[classified, "category"] == result.loc[classified, "true_category"]).mean()
        if classified.any() else float("nan")
    )
    print(
        f"{output_path}: tickets={len(result)} classified={int(classified.sum())} "
        f"accuracy={accuracy:.4f} tokens={spent} retries={retries} "
        f"statuses={result['status'].value_counts().to_dict()}"
    )
    return result


def main():
    os.chdir(ROOT)
    tickets = pd.read_csv("data/clean/tickets.csv", keep_default_na=False)
    customer_data = pd.read_csv("outputs/customer_segments.csv")
    segments = dict(zip(
        customer_data["customer_id"].astype(str),
        customer_data["segment_name"].astype(str),
    ))

    classify(tickets, segments, TOKEN_BUDGET, False, "outputs/triage_zero_shot.csv")
    classify(tickets, segments, TOKEN_BUDGET, True, "outputs/triage_results.csv")
    classify(tickets, segments, DEMO_BUDGET, False, "outputs/triage_budget_demo.csv")


if __name__ == "__main__":
    main()
