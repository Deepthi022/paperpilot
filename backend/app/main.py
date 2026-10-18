from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.mongodb import client
from app.routes import papers, search, chat, summaries, compare, notes

app = FastAPI(title="PaperPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router)
app.include_router(search.router)
app.include_router(chat.router)
app.include_router(summaries.router)
app.include_router(compare.router)
app.include_router(notes.router)

@app.get("/health")
def health():
    client.admin.command("ping")
    return {"status": "ok", "database": "connected"}