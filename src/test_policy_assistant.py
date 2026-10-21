
import os
import sys
import csv
import re

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)

from policy_assistant import answer_question

with open("data/raw/policy_eval.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

passed = 0

for row in rows:
    question = row["question"]
    expected_doc = row["expected_doc"].strip()
    expected_fact = row["expected_fact"].strip()

    answer, sources = answer_question(question)
    source_names = {r["source"] for r in sources}

    if expected_doc == "NONE":
        ok = (
            "insufficient" in answer.lower()
            or "don't know" in answer.lower()
            or "cannot answer" in answer.lower()
            or "not available" in answer.lower()
            or "could not find" in answer.lower()
        )
        status = "PASS" if ok else "CHECK"
    else:
        context = " ".join(r["text"] for r in sources).lower()
        fact = re.sub(r"[^a-z0-9]+", " ", expected_fact.lower()).strip()
        text = re.sub(r"[^a-z0-9]+", " ", context).strip()

        doc_ok = expected_doc in source_names
        fact_ok = fact in text
        status = "PASS" if doc_ok and fact_ok else "CHECK"
        ok = doc_ok and fact_ok

    passed += int(ok)

    print(f"\n{status}: {question}")
    print("Answer:", answer)
    print("Sources:", ", ".join(sorted(source_names)) or "None")

print(f"\nEvaluation checks passed: {passed}/{len(rows)}")
