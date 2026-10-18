import sys
from app.services.pdf_service import extract_pages

pages = extract_pages(sys.argv[1])
print(f"Extracted {len(pages)} pages")
for p in pages[:2]:
    print(f"\n--- Page {p['page']} ---")
    print(p["text"][:500])