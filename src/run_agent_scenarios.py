
import os
import sys
import json
import re
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import refund_agent

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)

os.makedirs("outputs", exist_ok=True)

scenarios = pd.read_csv("data/raw/agent_scenarios.csv").fillna("")
runs = []
ledger = []
original_tool = refund_agent.run_tool

def logged_tool(name, args):
    result = original_tool(name, args)

    if name == "issue_refund" and result.get("status") == "approved_for_mock_processing":
        ledger.append({
            "order_id": args.get("order_id"),
            "refund_inr": args.get("refund_inr"),
            "status": "simulated",
            "tool": name
        })

    return result

refund_agent.run_tool = logged_tool

try:
    for _, row in scenarios.iterrows():
        sid = str(row["scenario_id"])
        message = str(row["message"])
        response = refund_agent.run_agent(message)

        if response.startswith("ESCALATE: maximum agent steps reached."):
            outcome = "FALLBACK"
        elif response.startswith("REFUND:"):
            outcome = "REFUND"
        elif response.startswith("ESCALATE:"):
            outcome = "ESCALATE"
        elif response.startswith("DENIED:"):
            outcome = "DENIED"
        elif response.startswith("NOT_FOUND:"):
            outcome = "NOT_FOUND"
        else:
            outcome = "FALLBACK"

        expected = str(row["expected_outcome"])
        match = outcome == expected

        item = {
            "scenario_id": sid,
            "customer_id": str(row["customer_id"]),
            "message": message,
            "expected_outcome": expected,
            "actual_outcome": outcome,
            "passed": match,
            "response": response
        }

        runs.append(item)

        print(
            sid,
            "| expected:", expected,
            "| actual:", outcome,
            "| passed:", match
        )

finally:
    refund_agent.run_tool = original_tool

with open("outputs/agent_runs.jsonl", "w", encoding="utf-8") as f:
    for item in runs:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

with open("outputs/refund_ledger.jsonl", "w", encoding="utf-8") as f:
    for item in ledger:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")

print("\nScenarios:", len(runs))
print("Passed:", sum(item["passed"] for item in runs))
print("Failed:", sum(not item["passed"] for item in runs))
print("Simulated refunds:", len(ledger))
print("Saved outputs/agent_runs.jsonl")
print("Saved outputs/refund_ledger.jsonl")
