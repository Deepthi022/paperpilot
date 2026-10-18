import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database.mongodb import db

router = APIRouter(prefix="/notes", tags=["notes"])


class NoteIn(BaseModel):
    paper_id: str
    text: str


class NoteUpdate(BaseModel):
    text: str


def _out(n: dict) -> dict:
    n["note_id"] = n.pop("_id")
    return n


@router.get("")
def list_notes(paper_id: str | None = None):
    filt = {"paper_id": paper_id} if paper_id else {}
    return [_out(n) for n in db.notes.find(filt).sort("updated_at", -1)]


@router.post("")
def create_note(note: NoteIn):
    if not note.text.strip():
        raise HTTPException(400, "Note is empty")
    if not db.papers.find_one({"_id": note.paper_id}):
        raise HTTPException(404, "Paper not found")
    now = datetime.now(timezone.utc)
    doc = {
        "_id": str(uuid.uuid4()),
        "paper_id": note.paper_id,
        "text": note.text.strip(),
        "created_at": now,
        "updated_at": now,
    }
    db.notes.insert_one(doc)
    return _out(doc)


@router.put("/{note_id}")
def update_note(note_id: str, note: NoteUpdate):
    if not note.text.strip():
        raise HTTPException(400, "Note is empty")
    result = db.notes.find_one_and_update(
        {"_id": note_id},
        {"$set": {"text": note.text.strip(), "updated_at": datetime.now(timezone.utc)}},
        return_document=True,
    )
    if not result:
        raise HTTPException(404, "Note not found")
    return _out(result)


@router.delete("/{note_id}")
def delete_note(note_id: str):
    if db.notes.delete_one({"_id": note_id}).deleted_count == 0:
        raise HTTPException(404, "Note not found")
    return {"deleted": note_id}