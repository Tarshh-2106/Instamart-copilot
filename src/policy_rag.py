
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

folder = "data/policies"

def load_policies():
    docs = []

    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)

        if not os.path.isfile(path) or not name.endswith(".txt"):
            continue

        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        parts = re.split(r"(?<=[.!?])\s+", text)

        for part in parts:
            part = part.strip()

            if part and not part.lower().endswith(" policy."):
                docs.append({
                    "source": name,
                    "text": part
                })
    return docs

docs = load_policies()
texts = [d["text"] for d in docs]

vectorizer = TfidfVectorizer(stop_words="english")
matrix = vectorizer.fit_transform(texts)

def search_policy(question, k=5):
    q = vectorizer.transform([question])
    scores = cosine_similarity(q, matrix).flatten()
    ids = scores.argsort()[::-1][:k]

    results = []

    for i in ids:
        results.append({
            "source": docs[i]["source"],
            "text": docs[i]["text"],
            "score": round(float(scores[i]), 3)
        })

    return results

if __name__ == "__main__":
    print("Policy chunks loaded:", len(docs))
    print("Policy files:", len(set(d["source"] for d in docs)))

    while True:
        question = input("\nEnter a policy question (or 'exit'): ").strip()

        if question.lower() == "exit":
            break

        if not question:
            print("Please enter a question.")
            continue

        print("\nTop matching policy passages:")

        for result in search_policy(question):
            print(
                f"\nSource: {result['source']}"
                f"\nScore: {result['score']}"
                f"\n{result['text']}"
            )
