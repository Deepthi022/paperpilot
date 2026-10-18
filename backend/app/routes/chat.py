from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database.mongodb import db
from app.services.retrieval_service import search_chunks
from app.services.llm_service import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str
    paper_ids: list[str] | None = None
    top_k: int = 5


@router.post("")
def chat(req: ChatRequest):
    chunks = search_chunks(req.question, req.paper_ids, req.top_k)
    if not chunks:
        raise HTTPException(400, "No embedded papers found. Upload, chunk and embed a paper first.")

    try:
        answer = answer_question(req.question, chunks)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {type(e).__name__}: {str(e)[:300]}")

    ids = list({c["paper_id"] for c in chunks})
    names = {p["_id"]: p["filename"] for p in db.papers.find({"_id": {"$in": ids}})}

    sources = [
        {
            "ref": i,
            "paper_id": c["paper_id"],
            "filename": names.get(c["paper_id"]),
            "page": c["page"],
            "score": c["score"],
            "snippet": c["text"][:200],
        }
        for i, c in enumerate(chunks, start=1)
    ]
    return {"question": req.question, "answer": answer, "sources": sources}