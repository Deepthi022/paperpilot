import json
from app.database.mongodb import db
from app.services.llm_service import generate_text

MAX_CHARS = 30000  # per paper

COMPARE_PROMPT = (
    "You compare two research papers using ONLY the text provided. "
    "Return JSON in exactly this shape:\n"
    '{"rows": [{"aspect": "...", "paper_a": "...", "paper_b": "..."}], "overall": "..."}\n'
    "Use exactly these five aspects, in this order: Research problem, Method, "
    "Data or participants, Key findings, Limitations. "
    "Each cell is 1-3 plain-text sentences (no markdown) with page references like "
    "(p. 4) where useful. If a paper does not cover an aspect, say so instead of guessing. "
    '"overall" is 2-4 sentences on the main similarities and differences.'
)


def _paper_text(paper_id: str) -> str:
    pages = list(db.pages.find({"paper_id": paper_id}).sort("page", 1))
    text = "\n\n".join(f"[Page {p['page']}]\n{p['text']}" for p in pages)
    return text[:MAX_CHARS]


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


def compare_papers(id_a: str, id_b: str) -> dict | None:
    a = db.papers.find_one({"_id": id_a})
    b = db.papers.find_one({"_id": id_b})
    if not a or not b:
        return None

    contents = (
        f"=== PAPER A: {a['filename']} ===\n{_paper_text(id_a)}\n\n"
        f"=== PAPER B: {b['filename']} ===\n{_paper_text(id_b)}"
    )
    raw = generate_text(COMPARE_PROMPT, contents, max_tokens=4000, json_mode=True)
    data = _parse_json(raw)

    return {
        "paper_a": {"paper_id": id_a, "filename": a["filename"]},
        "paper_b": {"paper_id": id_b, "filename": b["filename"]},
        "rows": data.get("rows", []),
        "overall": data.get("overall", ""),
    }