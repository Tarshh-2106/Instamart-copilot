
import os
import json
from datetime import datetime, timezone

folder = "state"


def save_checkpoint(
    session_id, question, messages, step, scenario_id=None,
    tokens_used=0, tool_history=None, model_calls=0
):
    os.makedirs(folder, exist_ok=True)

    data = {
        "session_id": session_id,
        "question": question,
        "messages": messages,
        "step": step,
        "run_id": session_id,
        "scenario_id": scenario_id,
        "tokens_used": tokens_used,
        "tool_history": tool_history or [],
        "model_calls": model_calls,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    path = os.path.join(folder, f"{session_id}.json")
    temp = path + ".tmp"

    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    os.replace(temp, path)
    return path


def load_checkpoint(session_id):
    path = os.path.join(folder, f"{session_id}.json")

    if not os.path.isfile(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_checkpoint(session_id):
    path = os.path.join(folder, f"{session_id}.json")

    if os.path.isfile(path):
        os.remove(path)
        return True

    return False


if __name__ == "__main__":
    sid = input("Enter session ID: ").strip()

    if not sid or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in sid):
        print("Invalid session ID.")
    else:
        choice = input("Choose save, load, or delete: ").strip().lower()

        if choice == "save":
            question = input("Enter customer request: ")
            step = int(input("Enter current step: "))
            path = save_checkpoint(sid, question, [], step)
            print("Checkpoint saved:", path)

        elif choice == "load":
            data = load_checkpoint(sid)

            if data is None:
                print("No checkpoint found.")
            else:
                print(json.dumps(data, indent=2))

        elif choice == "delete":
            print("Checkpoint deleted." if delete_checkpoint(sid) else "No checkpoint found.")

        else:
            print("Invalid choice.")
