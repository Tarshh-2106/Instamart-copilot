import re


def redact(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[EMAIL]", text)
    text = re.sub(r"\b[6-9]\d{9}\b", "[PHONE]", text)
    text = re.sub(r"\bORD-\d{6}\b", "[ORDER_ID]", text, flags=re.IGNORECASE)
    return text


if __name__ == "__main__":
    for sample in (
        "Call 7766326255 about ORD-123456.",
        "Email help@example.com for assistance.",
    ):
        print("Original:", sample)
        print("Redacted:", redact(sample))
