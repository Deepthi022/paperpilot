import json
import sys
from pathlib import Path

from app.database.mongodb import db
from app.services.retrieval_service import search_chunks

TOP_K = 5


def main():
    path = Path(__file__).parent / "test_questions.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    paper = db.papers.find_one(
        {"filename": data["paper_filename"]}, sort=[("uploaded_at", -1)]
    )
    if not paper:
        sys.exit(f"Paper '{data['paper_filename']}' not found in the database.")
    paper_id = paper["_id"]

    questions = data["questions"]
    hit1 = hit3 = hit_k = kw_hits = 0
    reciprocal_ranks = []
    misses = []

    print(f"Evaluating {len(questions)} questions on {data['paper_filename']} (top_k={TOP_K})\n")

    for i, q in enumerate(questions, start=1):
        results = search_chunks(q["question"], [paper_id], TOP_K)
        pages = [r["page"] for r in results]
        expected = set(q["expected_pages"])

        rank = next((n for n, p in enumerate(pages, start=1) if p in expected), None)
        if rank == 1:
            hit1 += 1
        if rank is not None and rank <= 3:
            hit3 += 1
        if rank is not None:
            hit_k += 1
        reciprocal_ranks.append(1 / rank if rank else 0)

        joined = " ".join(r["text"] for r in results).lower()
        kw_ok = any(k.lower() in joined for k in q.get("keywords", []))
        kw_hits += kw_ok

        status = f"hit at rank {rank}" if rank else "MISS"
        print(f"{i:>2}. {status:<14} pages={pages} expected={sorted(expected)}  {q['question'][:60]}")
        if not rank:
            misses.append(q["question"])

    n = len(questions)
    print("\n--- Summary ---")
    print(f"Hit@1:  {hit1}/{n}  ({hit1 / n:.0%})")
    print(f"Hit@3:  {hit3}/{n}  ({hit3 / n:.0%})")
    print(f"Hit@{TOP_K}:  {hit_k}/{n}  ({hit_k / n:.0%})")
    print(f"MRR:    {sum(reciprocal_ranks) / n:.3f}")
    print(f"Keyword found in top {TOP_K}: {kw_hits}/{n}")
    if misses:
        print("\nMissed questions:")
        for m in misses:
            print(f" - {m}")


if __name__ == "__main__":
    main()