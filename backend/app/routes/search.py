from fastapi import APIRouter
from pydantic import BaseModel
from app.services.retrieval_service import search_chunks

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    paper_ids: list[str] | None = None
    top_k: int = 5


@router.post("")
def search(req: SearchRequest):
    return {"query": req.query, "results": search_chunks(req.query, req.paper_ids, req.top_k)}