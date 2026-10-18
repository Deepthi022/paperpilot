def chunk_pages(
    pages: list[dict],
    chunk_size: int = 200,
    overlap: int = 40,
    skip_references: bool = True,
) -> list[dict]:
    """Split page texts into overlapping word-based chunks, keeping page numbers.
    Stops at the 'References' heading so the bibliography isn't searched."""
    chunks = []
    index = 0
    for p in pages:
        words = p["text"].split()
        reached_refs = False

        if skip_references:
            for i, w in enumerate(words):
                if w == "References" and i + 1 < len(words) and words[i + 1][:1].isupper():
                    words = words[:i]
                    reached_refs = True
                    break

        start = 0
        while words and start < len(words):
            piece = words[start:start + chunk_size]
            chunks.append({
                "chunk_index": index,
                "page": p["page"],
                "text": " ".join(piece),
                "word_count": len(piece),
            })
            index += 1
            if start + chunk_size >= len(words):
                break
            start += chunk_size - overlap

        if reached_refs:
            break
    return chunks