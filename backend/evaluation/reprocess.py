from app.database.mongodb import db
from app.routes.papers import _chunk, _embed

paper = db.papers.find_one({"filename": "paper.pdf.pdf"}, sort=[("uploaded_at", -1)])
pid = paper["_id"]

chunks = _chunk(pid)
print("chunks:", len(chunks))

count, size = _embed(pid)
print("embedded:", count, "vectors of size", size)