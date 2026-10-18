import os
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pymongo import UpdateOne
from app.services.pdf_service import extract_pages
from app.services.chunking_service import chunk_pages
from app.services.embedding_service import embed_texts
from app.database.mongodb import db

router = APIRouter(prefix="/papers", tags=["papers"])

UPLOAD_DIR = "uploads"
MAX_SIZE_MB = 25


def _chunk(paper_id: str) -> list[dict]:
    pages = list(db.pages.find({"paper_id": paper_id}).sort("page", 1))
    chunks = chunk_pages(pages)
    db.chunks.delete_many({"paper_id": paper_id})  # safe to re-run
    if chunks:
        db.chunks.insert_many([{**c, "paper_id": paper_id} for c in chunks])
    db.papers.update_one(
        {"_id": paper_id},
        {"$set": {"status": "chunked", "chunk_count": len(chunks)}},
    )
    return chunks


def _embed(paper_id: str) -> tuple[int, int]:
    chunks = list(db.chunks.find({"paper_id": paper_id}).sort("chunk_index", 1))
    if not chunks:
        raise ValueError("Chunk the paper first")
    vectors = embed_texts([c["text"] for c in chunks])
    db.chunks.bulk_write([
        UpdateOne({"_id": c["_id"]}, {"$set": {"embedding": v}})
        for c, v in zip(chunks, vectors)
    ])
    db.papers.update_one({"_id": paper_id}, {"$set": {"status": "ready"}})
    return len(vectors), len(vectors[0])


@router.post("")
async def upload_paper(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are allowed")

    contents = await file.read()
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"File too large (max {MAX_SIZE_MB} MB)")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    paper_id = str(uuid.uuid4())
    path = os.path.join(UPLOAD_DIR, f"{paper_id}.pdf")
    with open(path, "wb") as f:
        f.write(contents)

    pages = extract_pages(path)
    if not pages:
        os.remove(path)
        raise HTTPException(422, "No text found. The PDF may be a scanned image.")

    db.papers.insert_one({
        "_id": paper_id,
        "filename": file.filename,
        "file_path": path,
        "page_count": len(pages),
        "status": "uploaded",
        "uploaded_at": datetime.now(timezone.utc),
    })
    db.pages.insert_many([
        {"paper_id": paper_id, "page": p["page"], "text": p["text"]}
        for p in pages
    ])

    try:
        chunks = _chunk(paper_id)
        _embed(paper_id)
    except Exception as e:
        db.papers.update_one({"_id": paper_id}, {"$set": {"status": "failed"}})
        raise HTTPException(500, f"Processing failed: {type(e).__name__}: {str(e)[:200]}")

    return {
        "paper_id": paper_id,
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(chunks),
        "status": "ready",
    }


@router.get("")
def list_papers():
    papers = list(
        db.papers.find({}, {"file_path": 0}).sort("uploaded_at", -1)
    )
    for p in papers:
        p["paper_id"] = p.pop("_id")
    return papers


@router.get("/{paper_id}")
def get_paper(paper_id: str):
    paper = db.papers.find_one({"_id": paper_id}, {"file_path": 0})
    if not paper:
        raise HTTPException(404, "Paper not found")
    paper["paper_id"] = paper.pop("_id")
    return paper


@router.get("/{paper_id}/file")
def get_paper_file(paper_id: str):
    paper = db.papers.find_one({"_id": paper_id})
    if not paper:
        raise HTTPException(404, "Paper not found")
    path = paper.get("file_path")
    if not path or not os.path.exists(path):
        raise HTTPException(404, "PDF file is missing on the server")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=paper["filename"],
        content_disposition_type="inline",  # open in the browser, don't download
    )


@router.delete("/{paper_id}")
def delete_paper(paper_id: str):
    paper = db.papers.find_one({"_id": paper_id})
    if not paper:
        raise HTTPException(404, "Paper not found")

    path = paper.get("file_path")
    if path and os.path.exists(path):
        os.remove(path)

    db.chunks.delete_many({"paper_id": paper_id})
    db.pages.delete_many({"paper_id": paper_id})
    db.notes.delete_many({"paper_id": paper_id})
    db.papers.delete_one({"_id": paper_id})
    return {"deleted": paper_id}


@router.post("/{paper_id}/chunk")
def chunk_paper(paper_id: str):
    if not db.papers.find_one({"_id": paper_id}):
        raise HTTPException(404, "Paper not found")
    chunks = _chunk(paper_id)
    return {
        "paper_id": paper_id,
        "chunk_count": len(chunks),
        "sample": chunks[0]["text"][:200] if chunks else "",
    }


@router.post("/{paper_id}/embed")
def embed_paper(paper_id: str):
    if not db.papers.find_one({"_id": paper_id}):
        raise HTTPException(404, "Paper not found")
    try:
        count, size = _embed(paper_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"paper_id": paper_id, "chunks_embedded": count, "vector_size": size}