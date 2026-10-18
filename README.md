# PaperPilot

An AI research paper assistant. Upload PDFs, ask questions and get answers with page-level citations, compare papers side by side, generate structured summaries, and keep notes per paper.

It is a retrieval-augmented generation (RAG) app: answers are written only from passages retrieved from your own papers, and every claim points back to a paper and page.

<!-- Add screenshots here: docs/screenshots/papers.png, chat.png, compare.png -->

## Features

- **My Papers**: upload PDFs; text is extracted, chunked and embedded automatically in one step
- **Chat with citations**: ask a question about one paper or all of them; answers cite sources as `[1]`, `[2]`, and each source card shows the paper, page and matching text
- **Compare**: pick two papers and get a table covering research problem, method, data, findings and limitations
- **Summaries**: structured summary per paper, cached in the database so it is generated once
- **Notes**: create, edit and delete notes per paper
- **Evaluation script**: measures retrieval quality (Hit@k, MRR) on a hand-written question set

## How it works

```
PDF upload
   |
   v
Extract text page by page (PyMuPDF) -> clean -> stop before the reference list
   |
   v
Split into overlapping ~200-word chunks (page number kept on every chunk)
   |
   v
Embed each chunk (fastembed, BAAI/bge-small-en-v1.5, 384 dims) -> store in MongoDB
   |
Question ----> embed query -> cosine similarity over chunks -> top 5 chunks
                                                                  |
                                                                  v
                                   Gemini writes an answer using ONLY those chunks,
                                   citing them as [1], [2] ... -> shown with page cards
```

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React (Vite), React Router |
| Backend | Python, FastAPI |
| Database | MongoDB (papers, pages, chunks, notes) |
| PDF parsing | PyMuPDF |
| Embeddings | fastembed (local, free, no API key) |
| Vector search | NumPy cosine similarity over stored vectors |
| LLM | Google Gemini API |

## Getting started

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB running locally (`mongodb://localhost:27017`)
- A Google Gemini API key from Google AI Studio

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

Create `backend/.env` (see `.env.example`):

```
MONGODB_URI=mongodb://localhost:27017
DB_NAME=paperpilot
GEMINI_API_KEY=your-key-here
```

Run it:

```bash
uvicorn app.main:app --reload --reload-dir app
```

API docs are at http://localhost:8000/docs.

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
```

Run it:

```bash
npm run dev
```

Open http://localhost:5173.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/papers` | Upload a PDF (extract, chunk, embed) |
| GET | `/papers` | List papers |
| POST | `/search` | Retrieve the most relevant chunks for a query |
| POST | `/chat` | Cited answer for a question |
| POST | `/summaries/{id}` | Structured summary (cached) |
| POST | `/compare` | Compare two papers |
|

## Evaluation

Retrieval decides answer quality, so it is measured directly. `evaluation/run_eval.py` runs a set of questions from `evaluation/test_questions.json` (each with the page that contains the answer) through the same search the chat uses, and reports:

- **Hit@k**: share of questions where a correct page is in the top k results
- **MRR**: mean reciprocal rank of the first correct page (1.0 is perfect)

```bash
cd backend
python -m evaluation.run_eval
```

### Results

Baseline on 5 questions (replace with the numbers from your larger question set):

| Change | Hit@1 | Hit@5 | MRR |
|---|---|---|---|
| Baseline (everything indexed) | 20% | 80% | 0.440 |
| Skip the reference list when chunking | 40% | 80% | 0.550 |

Finding: the bibliography was matching queries on title words alone and crowding out real answers. Excluding it from the index raised both Hit@1 and MRR.

## Project structure

```
paperpilot/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/        papers, search, chat, summaries, compare, notes
│   │   ├── services/      pdf, chunking, embedding, retrieval, llm, summary, comparison
│   │   └── database/      mongodb.py
│   ├── evaluation/        run_eval.py, test_questions.json
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/    Sidebar, CitationCard
│       ├── pages/         MyPapers, ResearchChat, ComparePapers, Summaries, Notes
│       └── services/      api.js
└── README.md
```

## Known limitations

- Scanned (image-only) PDFs are rejected because there is no OCR step
- The embedding model is English-only, so non-English papers will search poorly
- Questions about document structure (for example "what are the keywords?") can miss, because meaning-based search does not match short labels well
- Reference-list detection is a heuristic that looks for a "References" heading
- No user accounts: all papers are shared in one library

## Roadmap

- Hybrid search (keyword + embeddings) and reranking
- Clickable citations that open the PDF at the cited page
- Multilingual embeddings and OCR for scanned papers
- User accounts, background processing for large uploads, Docker Compose