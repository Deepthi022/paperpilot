from fastapi import APIRouter, HTTPException
from app.services.summary_service import summarize_paper

router = APIRouter(prefix="/summaries", tags=["summaries"])


@router.post("/{paper_id}")
def summarize(paper_id: str, refresh: bool = False):
    try:
        result = summarize_paper(paper_id, refresh)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {type(e).__name__}: {str(e)[:300]}")
    if result is None:
        raise HTTPException(404, "Paper not found")
    return {"paper_id": paper_id, **result}