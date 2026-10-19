
import os
import re

path = "mock_llm.py"

with open(path, "r", encoding="utf-8") as f:
    text = f.read()

start = text.find("def _policy(")
end = text.find("\ndef _agent(", start)

if start == -1:
    print("Could not find _policy function.")
elif end == -1:
    print(text[start:])
else:
    print(text[start:end])
