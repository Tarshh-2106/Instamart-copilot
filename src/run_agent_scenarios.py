
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
active_trace = []
original_tool = refund_agent.run_tool

def logged_tool(name, args):
    result = original_tool(name, args)
    active_trace.append({
        "name": name,
        "arguments": args,
        "result": result
    })

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
        active_trace.clear()
        sid = str(row["scenario_id"])
        message = str(row["message"])
        response = refund_agent.run_agent(message, scenario_id=sid)

        if response.startswith("FALLBACK_MAX_ITERATIONS:"):
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
        actual_refund = next(
            (
                float(call["result"]["refund_inr"])
                for call in active_trace
                if call["name"] in {"calculate_refund", "issue_refund", "escalate_to_human"}
                and "refund_inr" in call["result"]
            ),
            0.0,
        )

        item = {
            "scenario_id": sid,
            "customer_id": str(row["customer_id"]),
            "message": message,
            "expected_outcome": expected,
            "expected_refund_inr": float(row["expected_refund_inr"]),
            "actual_outcome": outcome,
            "actual_refund_inr": actual_refund,
            "passed": match,
            "response": response,
            "status": refund_agent.LAST_RUN.get("status"),
            "model_calls": refund_agent.LAST_RUN.get("model_calls"),
            "tokens_used": refund_agent.LAST_RUN.get("tokens_used"),
            "tools_executed": refund_agent.LAST_RUN.get("tool_history", []),
            "tool_trace": list(active_trace)
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
