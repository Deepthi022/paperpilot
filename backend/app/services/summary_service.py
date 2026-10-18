from datetime import datetime, timezone
from app.database.mongodb import db
from app.services.llm_service import generate_text

MAX_CHARS = 60000  # keeps very long papers within limits

SUMMARY_PROMPT = (
    "Summarize this research paper using ONLY the paper text provided. "
    "Write plain text with no markdown symbols (no asterisks, no # headings). "
    "Use exactly these four section labels, each on its own line followed by 2-4 sentences:\n"
    "Problem:\nMethod:\nKey findings:\nLimitations:\n"
    "Mention page numbers like (p. 4) where useful. "
    "If the paper does not cover a section, say so instead of guessing."
)


def summarize_paper(paper_id: str, refresh: bool = False) -> dict | None:
    paper = db.papers.find_one({"_id": paper_id})
    if not paper:
        return None

    if paper.get("summary") and not refresh:
        return {"summary": paper["summary"], "cached": True}

    pages = list(db.pages.find({"paper_id": paper_id}).sort("page", 1))
    text = "\n\n".join(f"[Page {p['page']}]\n{p['text']}" for p in pages)[:MAX_CHARS]

    summary = generate_text(SUMMARY_PROMPT, text, max_tokens=2000)
    db.papers.update_one(
        {"_id": paper_id},
        {"$set": {"summary": summary, "summary_at": datetime.now(timezone.utc)}},
    )
    return {"summary": summary, "cached": False}