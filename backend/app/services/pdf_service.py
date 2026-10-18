import pymupdf
from app.utils.text_cleaner import clean_text

def extract_pages(file_path: str) -> list[dict]:
    """Return a list like [{"page": 1, "text": "..."}, ...]"""
    pages = []
    with pymupdf.open(file_path) as doc:
        for i, page in enumerate(doc, start=1):
            text = clean_text(page.get_text())
            if text:  # skip blank pages
                pages.append({"page": i, "text": text})
    return pages