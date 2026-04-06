# utils/chunking.py
# Splits long text into paragraph-sized chunks for downstream processing.
# Used by all three scrapers to fill the content_chunks field.

def chunk_text(text, min_length=100):
    if not text:
        return []

    # Try splitting on double newlines first
    raw_chunks = text.split("\n\n")

    # If that gives only 1 chunk, try single newlines
    if len(raw_chunks) <= 1:
        raw_chunks = text.split("\n")

    # If still 1 chunk, split by sentences (every ~500 chars)
    if len(raw_chunks) <= 1:
        words = text.split()
        raw_chunks = []
        current = []
        for word in words:
            current.append(word)
            if len(chr(32).join(current)) > 500:
                raw_chunks.append(" ".join(current))
                current = []
        if current:
            raw_chunks.append(" ".join(current))

    chunks = []
    for chunk in raw_chunks:
        cleaned = " ".join(chunk.split())
        if len(cleaned) >= min_length:
            chunks.append(cleaned)

    return chunks
