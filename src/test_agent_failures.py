

import os
import sys
import csv

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
os.chdir(root)

import mock_llm
from refund_agent import run_agent

with open("data/raw/agent_scenarios.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

row = next(r for r in rows if r["scenario_id"] == "S1")
question = row["message"]

original_chat = mock_llm.chat

class TokenLimitError(Exception):
    pass

def token_limit(*args, **kwargs):
    raise TokenLimitError("Simulated token limit exceeded")

def timeout(*args, **kwargs):
    raise TimeoutError("Simulated agent timeout")

try:
    mock_llm.chat = token_limit
    result1 = run_agent(question)
    print("Token-limit response:", result1)
    print("Token-limit fallback:", result1.startswith("SAFE_FALLBACK"))
    print("Token-limit reason included:", "TokenLimitError" in result1)

    mock_llm.chat = timeout
    result2 = run_agent(question)
    print("\nTimeout response:", result2)
    print("Timeout fallback:", result2.startswith("SAFE_FALLBACK"))
    print("Timeout reason included:", "TimeoutError" in result2)

finally:
    mock_llm.chat = original_chat

print("\nOriginal mock restored:", mock_llm.chat is original_chat)
