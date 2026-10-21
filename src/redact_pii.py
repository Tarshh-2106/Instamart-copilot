
import re

def redact(text):
    if not isinstance(text, str):
        return ""

    text = re.sub(
        r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
        "[EMAIL]",
        text
    )

    text = re.sub(
        r"(?<!\w)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\w)",
        "[PHONE]",
        text
    )

    text = re.sub(
        r"\bORD-\d{6}\b",
        "[ORDER_ID]",
        text,
        flags=re.IGNORECASE
    )

    return text

if __name__ == "__main__":
    samples = [
        "Call 7766326255 about my order.",
        "Email help@example.com for assistance.",
        "Refund for ORD-123456, call 9562272031 or email customer@example.com."
    ]

    for s in samples:
        print("Original:", s)
        print("Redacted:", redact(s))
        print()
