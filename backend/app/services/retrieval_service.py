import numpy as np
from app.database.mongodb import db
from app.services.embedding_service import embed_query


def search_chunks(query: str, paper_ids: list[str] | None = None, top_k: int = 5) -> list[dict]:
    filt = {"embedding": {"$exists": True}}
    if paper_ids:
        filt["paper_id"] = {"$in": paper_ids}

    chunks = list(db.chunks.find(filt))
    if not chunks:
        return []

    matrix = np.array([c["embedding"] for c in chunks])
    q = np.array(embed_query(query))

    # cosine similarity
    scores = (matrix @ q) / (np.linalg.norm(matrix, axis=1) * np.linalg.norm(q))
    top = np.argsort(scores)[::-1][:top_k]

    results = []
    for i in top:
        c = chunks[i]
        results.append({
            "paper_id": c["paper_id"],
            "page": c["page"],
            "score": round(float(scores[i]), 4),
            "text": c["text"],
        })
    return results