import os
import json
import uuid

from agent_checkpoint import save_checkpoint, load_checkpoint, delete_checkpoint
from refund_agent import run_agent

sid = "recovery_test_" + uuid.uuid4().hex[:8]
question = "Check the refund status for order ORD-110227"

try:
    path = save_checkpoint(sid, question, [], 2)
    saved = load_checkpoint(sid)

    print("Checkpoint saved:", os.path.isfile(path))
    print("Session ID matches:", saved["session_id"] == sid)
    print("Question matches:", saved["question"] == question)
    print("Step restored:", saved["step"] == 2)

    mismatch = run_agent("A different refund request", session_id=sid, resume=True)
    print("Mismatched request rejected:", mismatch.startswith("SAFE_FALLBACK"))

    missing = run_agent(question, session_id="missing_recovery_test", resume=True)
    print("Missing checkpoint handled:", missing.startswith("NOT_FOUND"))

    empty = run_agent(question, session_id=sid, resume=True)
    print("Empty history handled:", empty.startswith("SAFE_FALLBACK"))

finally:
    removed = delete_checkpoint(sid)
    print("Test checkpoint cleaned up:", removed)