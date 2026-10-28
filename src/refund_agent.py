
import os
import sys
import json
import sqlite3
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mock_llm
from policy_rag import search_policy
from agent_checkpoint import save_checkpoint, load_checkpoint, delete_checkpoint

db = "data/instamart.db"
max_steps = 6
LAST_RUN = {}


def get_order(order_id):
    if not isinstance(order_id, str) or not order_id.strip():
        return {"error": "Invalid order ID"}

    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row

    try:
        row = con.execute(
            """
            SELECT order_id, customer_id, product_id, quantity,
                   status, order_amount, delivery_minutes
            FROM orders
            WHERE order_id = ?
            ORDER BY CASE WHEN status = 'completed' THEN 0 ELSE 1 END
            LIMIT 1
            """,
            (order_id.strip(),)
        ).fetchone()

        if row is None:
            return {"error": "Order not found"}

        data = dict(row)

        for key in ("order_amount", "delivery_minutes"):
            if data[key] is not None:
                data[key] = float(data[key])

        return data
    finally:
        con.close()


def calculate_refund(order_amount, delivery_minutes):
    try:
        amount = float(order_amount)
        minutes = float(delivery_minutes)
    except (TypeError, ValueError):
        return {"error": "Invalid order amount or delivery time"}

    if amount < 0 or minutes < 0:
        return {"error": "Invalid negative value"}

    refund = amount if minutes > 45 else 0

    return {"refund_inr": round(refund, 2)}



def search_policy_tool(args):
    query = args.get("query", "")

    if not isinstance(query, str) or not query.strip():
        return {"error": "Policy query is required"}

    results = search_policy(query, k=3)

    if not results or results[0]["score"] == 0:
        return {"error": "No relevant policy information found"}

    return {
        "results": [
            {
                "source": r["source"],
                "text": r["text"],
                "score": r["score"]
            }
            for r in results
        ]
    }


def issue_refund(args):
    order_id = args.get("order_id")
    order = get_order(order_id)
    if "error" in order or order["status"] != "completed":
        return {"error": "Only completed orders can receive a refund"}
    eligible = calculate_refund(order["order_amount"], order["delivery_minutes"])
    try:
        requested = round(float(args.get("refund_inr")), 2)
    except (TypeError, ValueError):
        return {"error": "Invalid refund amount"}
    if eligible.get("refund_inr") != requested or requested > 1000:
        return {"error": "Refund is not eligible for automatic processing"}
    return {
        "status": "approved_for_mock_processing",
        "order_id": order_id,
        "refund_inr": requested
    }


def escalate_to_human(args):
    order_id = args.get("order_id")
    try:
        amount = round(float(args.get("refund_inr")), 2)
    except (TypeError, ValueError):
        return {"error": "Invalid refund amount"}
    order = get_order(order_id)
    if "error" in order or order["status"] != "completed":
        return {"error": "Only completed orders can be escalated for a refund"}
    eligible = calculate_refund(order["order_amount"], order["delivery_minutes"])
    if amount <= 1000 or eligible.get("refund_inr") != amount:
        return {"error": "Only eligible refunds above INR 1000 require escalation"}
    return {
        "status": "escalation_recorded",
        "order_id": order_id,
        "refund_inr": amount
    }


def calculate_refund_tool(args):
    return calculate_refund(
        args.get("order_amount"),
        args.get("delivery_minutes")
    )


TOOL_MAP = {
    "get_order": lambda args: get_order(args.get("order_id")),
    "search_policy": search_policy_tool,
    "calculate_refund": calculate_refund_tool,
    "issue_refund": issue_refund,
    "escalate_to_human": escalate_to_human
}

TOOLS_SPEC = [
        {
            "type": "function",
            "function": {
                "name": "get_order",
                "description": "Look up an order using its order ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string"}
                    },
                    "required": ["order_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_policy",
                "description": "Retrieve refund policy information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_refund",
                "description": "Calculate an eligible refund.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_amount": {"type": "number"},
                        "delivery_minutes": {
                            "type": ["number", "null"]
                        }
                    },
                    "required": ["order_amount", "delivery_minutes"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "issue_refund",
                "description": "Record a simulated refund.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string"},
                        "refund_inr": {"type": "number"}
                    },
                    "required": ["order_id", "refund_inr"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "escalate_to_human",
                "description": "Record escalation to a human support lead.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string"},
                        "refund_inr": {"type": "number"}
                    },
                    "required": ["order_id", "refund_inr"]
                }
            }
        }
]

def run_tool(name, args):
    if not isinstance(args, dict):
        return {"error": "Tool arguments must be an object"}

    tool = TOOL_MAP.get(name)

    if tool is None:
        return {"error": "Unknown tool"}

    return tool(args)



def run_agent(
    user_message, scenario_id=None, max_iterations=6, token_limit=6000,
    time_limit_seconds=10, session_id=None, resume=False
):
    global LAST_RUN
    question = user_message
    if not isinstance(question, str) or not question.strip():
        LAST_RUN = {"status": "NEEDS_INFO", "model_calls": 0, "tokens_used": 0, "tool_history": []}
        return "NEEDS_INFO: please describe your refund request."

    mock_llm.reset()
    started = time.monotonic()
    run_id = session_id or scenario_id or uuid.uuid4().hex
    tokens_used = 0
    model_calls = 0
    tool_history = []

    if resume:
        if not session_id and not scenario_id:
            LAST_RUN = {"status": "NEEDS_INFO", "model_calls": 0, "tokens_used": 0, "tool_history": []}
            return "NEEDS_INFO: session ID required to resume."

        run_id = session_id or scenario_id
        saved = load_checkpoint(run_id)

        if saved is None:
            LAST_RUN = {"status": "NOT_FOUND", "model_calls": 0, "tokens_used": 0, "tool_history": []}
            return "NOT_FOUND: no saved checkpoint for this session."

        if saved.get("question") != question.strip():
            LAST_RUN = {"status": "SAFE_FALLBACK", "model_calls": 0, "tokens_used": 0, "tool_history": []}
            return "SAFE_FALLBACK: request does not match saved session."
        if (
            scenario_id is not None
            and saved.get("scenario_id") is not None
            and saved.get("scenario_id") != scenario_id
        ):
            LAST_RUN = {"status": "SAFE_FALLBACK", "model_calls": 0, "tokens_used": 0, "tool_history": []}
            return "SAFE_FALLBACK: scenario does not match saved session."

        messages = saved.get("messages", [])

        if not messages:
            LAST_RUN = {"status": "SAFE_FALLBACK", "model_calls": 0, "tokens_used": 0, "tool_history": []}
            return "SAFE_FALLBACK: checkpoint has no conversation history."

        start_step = saved.get("step", 0)
        tokens_used = saved.get("tokens_used", 0)
        model_calls = saved.get("model_calls", 0)
        tool_history = saved.get("tool_history", [])
        scenario_id = saved.get("scenario_id", scenario_id)
    else:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an Instamart refund support AGENT. "
                    "Use the tools to check orders and policies. "
                    "Only completed orders can be refunded. "
                    "Refunds apply only when delivery takes more than 45 minutes. "
                    "Refunds above INR 1000 require human escalation. "
                    "This is a mock system; do not claim real money was transferred."
                )
            },
            {"role": "user", "content": question.strip()}
        ]

        start_step = 0

    if run_id and not resume:
        save_checkpoint(
            run_id, question.strip(), messages, start_step, scenario_id,
            tokens_used, tool_history, model_calls
        )

    if max_iterations < 1 or token_limit < 1 or time_limit_seconds <= 0:
        LAST_RUN = {
            "status": "SAFE_FALLBACK", "model_calls": model_calls,
            "tokens_used": tokens_used, "tool_history": tool_history,
            "run_id": run_id, "scenario_id": scenario_id,
        }
        return "SAFE_FALLBACK: limits must be positive."

    for step in range(start_step, max_iterations):
        if tokens_used >= token_limit:
            LAST_RUN = {
                "status": "FALLBACK_TOKEN_LIMIT", "model_calls": model_calls,
                "tokens_used": tokens_used, "tool_history": tool_history,
                "run_id": run_id, "scenario_id": scenario_id,
            }
            return "FALLBACK_TOKEN_LIMIT: support agent token limit reached."
        if time.monotonic() - started >= time_limit_seconds:
            LAST_RUN = {
                "status": "FALLBACK_TIME_LIMIT", "model_calls": model_calls,
                "tokens_used": tokens_used, "tool_history": tool_history,
                "run_id": run_id, "scenario_id": scenario_id,
            }
            return "FALLBACK_TIME_LIMIT: support agent time limit reached."
        try:
            response = mock_llm.chat(messages, tools=TOOLS_SPEC)
            model_calls += 1
            call_tokens = response.usage.total_tokens
            if tokens_used + call_tokens > token_limit:
                LAST_RUN = {
                    "status": "FALLBACK_TOKEN_LIMIT", "model_calls": model_calls,
                    "tokens_used": tokens_used, "tool_history": tool_history,
                    "run_id": run_id, "scenario_id": scenario_id,
                }
                return "FALLBACK_TOKEN_LIMIT: support agent token limit reached."
            tokens_used += call_tokens
            message = response.choices[0].message
        except Exception as e:
            model_calls += 1
            kind = type(e).__name__
            LAST_RUN = {
                "status": "SAFE_FALLBACK", "model_calls": model_calls,
                "tokens_used": tokens_used, "tool_history": tool_history,
                "run_id": run_id, "scenario_id": scenario_id,
            }
            return f"SAFE_FALLBACK: agent call failed ({kind})."

        if time.monotonic() - started >= time_limit_seconds:
            LAST_RUN = {
                "status": "FALLBACK_TIME_LIMIT", "model_calls": model_calls,
                "tokens_used": tokens_used, "tool_history": tool_history,
                "run_id": run_id, "scenario_id": scenario_id,
            }
            return "FALLBACK_TIME_LIMIT: support agent time limit reached."

        calls = getattr(message, "tool_calls", None)

        if not calls:
            result = message.content or "SAFE_FALLBACK: no agent response."
            status = result.split(":", 1)[0].strip().replace(" ", "_").upper()
            LAST_RUN = {
                "status": status, "model_calls": model_calls,
                "tokens_used": tokens_used, "tool_history": tool_history,
                "run_id": run_id, "scenario_id": scenario_id,
            }
            return result

        for call in calls:
            try:
                args = call.arguments
                if isinstance(args, str):
                    args = json.loads(args)
                tool_history.append(call.name)
                result = run_tool(call.name, args)
            except (json.JSONDecodeError, TypeError, ValueError):
                result = {"error": "Invalid tool arguments"}
            except Exception as e:
                result = {"error": f"Tool failed: {type(e).__name__}"}

            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.name,
                            "arguments": call.arguments
                        }
                    }
                ]
            })

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "name": call.name,
                "content": json.dumps(result)
            })

            if run_id:
                save_checkpoint(
                    run_id,
                    question.strip(),
                    messages,
                    step + 1,
                    scenario_id,
                    tokens_used,
                    tool_history,
                    model_calls
                )

    summary = []

    for m in messages:
        if m["role"] == "user":
            summary.append("Customer request: " + m["content"])
        elif m["role"] == "tool":
            summary.append(m["name"] + ": " + m["content"])

    summary = "\n".join(summary[-6:])

    LAST_RUN = {
        "status": "FALLBACK_MAX_ITERATIONS", "model_calls": model_calls,
        "tokens_used": tokens_used, "tool_history": tool_history,
        "run_id": run_id, "scenario_id": scenario_id,
    }
    return (
        "FALLBACK_MAX_ITERATIONS: maximum agent steps reached. "
        "Human support handoff required.\n"
        "Case summary:\n" + summary
    )


if __name__ == "__main__":
    while True:
        question = input("\nEnter refund request (or 'exit'): ").strip()

        if question.lower() == "exit":
            break

        print("\nAgent response:")
        print(run_agent(question))
