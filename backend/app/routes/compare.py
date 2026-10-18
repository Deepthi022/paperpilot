from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.comparison_service import compare_papers

router = APIRouter(prefix="/compare", tags=["compare"])


class CompareRequest(BaseModel):
    paper_ids: list[str]


@router.post("")
def compare(req: CompareRequest):
    if len(req.paper_ids) != 2 or req.paper_ids[0] == req.paper_ids[1]:
        raise HTTPException(400, "Choose exactly two different papers")
    try:
        result = compare_papers(req.paper_ids[0], req.paper_ids[1])
    except Exception as e:
        raise HTTPException(500, f"Compare error: {type(e).__name__}: {str(e)[:300]}")
    if result is None:
        raise HTTPException(404, "Paper not found")
    return result