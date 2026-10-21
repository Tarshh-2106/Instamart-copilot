
import os
import re
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder = os.path.join(root, "data", "policies")
eval_file = os.path.join(root, "data", "raw", "policy_eval.csv")

def load_chunks(step):
    docs = []

    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)

        if not os.path.isfile(path) or not name.endswith(".txt"):
            continue

        with open(path, encoding="utf-8") as f:
            words = f.read().split()

        for start in range(0, len(words), step):
            chunk = words[start:start + 40]

            if chunk:
                docs.append({
                    "source": name,
                    "text": " ".join(chunk)
                })

    return docs

def search(question, docs, vectorizer, matrix, k=3):
    q = vectorizer.transform([question])
    scores = cosine_similarity(q, matrix).flatten()
    ids = scores.argsort()[::-1]
    results = []

    for i in ids:
        if scores[i] <= 0:
            continue

        results.append(docs[i])

        if len(results) == k:
            break

    return results

def normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()

with open(eval_file, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

for label, step in [("10-word overlap", 30), ("Zero overlap", 40)]:
    docs = load_chunks(step)
    texts = [d["text"] for d in docs]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)

    doc_hits = 0
    fact_hits = 0
    fallback_hits = 0
    answerable = 0
    unanswerable = 0

    print(f"\n{'=' * 60}")
    print(label)
    print("Chunks:", len(docs))

    for row in rows:
        question = row["question"]
        expected_doc = row["expected_doc"].strip()
        expected_fact = row["expected_fact"].strip()
        results = search(question, docs, vectorizer, matrix)

        sources = {r["source"] for r in results}
        context = normalize(" ".join(r["text"] for r in results))

        if expected_doc == "NONE":
            unanswerable += 1
            passed = len(results) == 0
            fallback_hits += int(passed)
            print(f"FALLBACK {'PASS' if passed else 'CHECK'}: {question}")
            continue

        answerable += 1
        doc_ok = expected_doc in sources
        fact_ok = normalize(expected_fact) in context

        doc_hits += int(doc_ok)
        fact_hits += int(fact_ok)

        print(
            f"{'PASS' if doc_ok else 'FAIL'} DOC | "
            f"{'PASS' if fact_ok else 'CHECK'} FACT | "
            f"{question}"
        )

    print("\nDocument hits:", doc_hits, "/", answerable)
    print("Fact hits in retrieved context:", fact_hits, "/", answerable)
    print("Safe retrieval fallbacks:", fallback_hits, "/", unanswerable)
