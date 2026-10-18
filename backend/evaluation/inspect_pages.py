from app.database.mongodb import db

paper = db.papers.find_one({"filename": "paper.pdf.pdf"}, sort=[("uploaded_at", -1)])
pid = paper["_id"]

print("Total chunks in DB:", db.chunks.count_documents({"paper_id": pid}))
print("Chunks per page:")
for page in range(1, paper["page_count"] + 1):
    n = db.chunks.count_documents({"paper_id": pid, "page": page})
    print(f"  page {page}: {n}")

for page in (9, 10, 11):
    doc = db.pages.find_one({"paper_id": pid, "page": page})
    if not doc:
        continue
    text = doc["text"]
    print(f"\n=== Page {page} ({len(text.split())} words) ===")
    print(text[:400])
    print("... 'References' at char:", text.find("References"),
          "| 'REFERENCES' at char:", text.find("REFERENCES"))