
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

    return text

if __name__ == "__main__":
    samples = [
        "Call 7766326255 about my order.",
        "Email help@example.com for assistance.",
        "Call me on 9562272031 or email customer@example.com."
    ]

    for s in samples:
        print("Original:", s)
        print("Redacted:", redact(s))
        print()
