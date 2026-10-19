
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mock_llm
from policy_rag import search_policy

def answer_question(question):
    results = search_policy(question, k=3)

    context = "\n".join(
        f"Source: {r['source']}\nPolicy: {r['text']}"
        for r in results
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an Instamart policy assistant. "
                "Answer only from the supplied policy context. "
                "If the context does not contain the answer, say "
                "the policy information is insufficient. "
                "Do not invent policy rules."
            )
        },
        {
            "role": "user",
            "content": f"CONTEXT:\n{context}\nQUESTION:\n{question}"
        }
    ]

    response = mock_llm.chat(messages)
    return response.choices[0].message.content, results

if __name__ == "__main__":
    while True:
        question = input("\nAsk a policy question (or 'exit'): ").strip()

        if question.lower() == "exit":
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            answer, sources = answer_question(question)

            print("\nAssistant response:")
            print(answer)

            print("\nRetrieved sources:")
            for source in sources:
                print(f"- {source['source']} (score: {source['score']})")

        except Exception as e:
            print("Unable to answer the question:", str(e))
