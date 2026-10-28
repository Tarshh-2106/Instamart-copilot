

import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
folder = os.path.join(root, "data", "policies")

def load_policies():
    docs = []

    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)

        if not os.path.isfile(path) or not name.endswith(".txt"):
            continue

        with open(path, "r", encoding="utf-8") as f:
            words = f.read().split()

        for start in range(0, len(words), 30):
            chunk = words[start:start + 40]

            if chunk:
                docs.append({
                    "source": name,
                    "text": " ".join(chunk)
                })

    return docs

docs = load_policies()
texts = [d["text"] for d in docs]

vectorizer = TfidfVectorizer()
matrix = vectorizer.fit_transform(texts)

def search_policy(question, k=5):
    q = vectorizer.transform([question])
    scores = cosine_similarity(q, matrix).flatten()
    ids = scores.argsort()[::-1]

    results = []

    for i in ids:
        if scores[i] <= 0:
            continue

        results.append({
            "source": docs[i]["source"],
            "text": docs[i]["text"],
            "score": round(float(scores[i]), 3)
        })

        if len(results) == k:
            break

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

        results = search_policy(question)

        if not results:
            print("No relevant policy passages found.")
            continue

        print("\nTop matching policy passages:")

        for result in results:
            print(
                f"\nSource: {result['source']}"
                f"\nScore: {result['score']}"
                f"\n{result['text']}"
            )
