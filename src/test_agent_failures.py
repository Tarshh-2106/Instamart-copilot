import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
os.chdir(root)

from refund_agent import run_agent, LAST_RUN

question = "Please refund order ORD-100048"

token_result = run_agent(question, scenario_id="token_limit_demo", token_limit=1)
token_status = token_result.startswith("FALLBACK_TOKEN_LIMIT:")
print("Token-limit status:", token_result.split(":", 1)[0])
print("Token-limit fallback:", token_status)

time_result = run_agent(
    question, scenario_id="time_limit_demo", time_limit_seconds=0.0000000001
)
time_status = time_result.startswith("FALLBACK_TIME_LIMIT:")
print("Time-limit status:", time_result.split(":", 1)[0])
print("Time-limit fallback:", time_status)

loop_result = run_agent(
    "[LOOP] Refund order ORD-100048",
    scenario_id="max_iterations_demo",
    max_iterations=2,
)
iteration_status = loop_result.startswith("FALLBACK_MAX_ITERATIONS:")
print("Iteration-limit status:", loop_result.split(":", 1)[0])
print("Iteration-limit fallback:", iteration_status)

if not (token_status and time_status and iteration_status):
    raise AssertionError("A stop-safely demonstration did not reach its expected status")
