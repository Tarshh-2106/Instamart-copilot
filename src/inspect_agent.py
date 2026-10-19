
import os

path = "mock_llm.py"

with open(path, "r", encoding="utf-8") as f:
    text = f.read()

start = text.find("def _agent(")
end = text.find("\ndef chat(", start)

if start == -1:
    print("Could not find _agent function.")
elif end == -1:
    print(text[start:])
else:
    print(text[start:end])
