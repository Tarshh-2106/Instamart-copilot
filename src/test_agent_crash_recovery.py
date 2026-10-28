
import os
import sys
import csv
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import refund_agent
from agent_checkpoint import delete_checkpoint

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)

with open("data/raw/agent_scenarios.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

row = next(r for r in rows if r["scenario_id"] == "S1")
question = row["message"]
sid = "crash_recovery_" + uuid.uuid4().hex[:8]

tool_history = []
save_count = 0
crashed = False

original_tool = refund_agent.run_tool
original_save = refund_agent.save_checkpoint

def tracked_tool(name, args):
    result = original_tool(name, args)
    tool_history.append(name)
    return result

def crash_save(
    session_id, question, messages, step, scenario_id=None,
    tokens_used=0, tool_history=None, model_calls=0
):
    global save_count, crashed

    path = original_save(
        session_id, question, messages, step, scenario_id,
        tokens_used, tool_history, model_calls
    )
    save_count += 1

    if save_count == 3 and not crashed:
        crashed = True
        raise RuntimeError("Simulated crash after second tool checkpoint")

    return path

try:
    refund_agent.run_tool = tracked_tool
    refund_agent.save_checkpoint = crash_save

    try:
        refund_agent.run_agent(question, session_id=sid)
    except RuntimeError as e:
        print("Crash simulated:", str(e))

    refund_agent.save_checkpoint = original_save

    print("Tools completed before crash:", tool_history)
    print("Crash occurred after two tools:", crashed and len(tool_history) == 2)

    if not crashed or len(tool_history) != 2:
        raise RuntimeError("Crash was not simulated at the expected point")

    result = refund_agent.run_agent(question, session_id=sid, resume=True)

    print("Resumed response:", result)
    print("Complete tool history:", tool_history)

    expected = [
        "get_order",
        "search_policy",
        "calculate_refund",
        "issue_refund"
    ]

    print("Tool order correct:", tool_history == expected)
    print("Exactly four tool executions:", len(tool_history) == 4)
    print("Refund outcome correct:", result.startswith("REFUND:"))

finally:
    refund_agent.run_tool = original_tool
    refund_agent.save_checkpoint = original_save
    print("Checkpoint cleaned up:", delete_checkpoint(sid))
