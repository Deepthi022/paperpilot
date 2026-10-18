import { useState } from "react";
import { getSummary } from "../services/api";

export default function Summaries({ papers, onError }) {
  const [results, setResults] = useState({}); // paper_id -> summary text
  const [loadingId, setLoadingId] = useState("");

  const ready = papers.filter((p) => p.status === "ready");

  async function summarize(paperId, refresh) {
    onError("");
    setLoadingId(paperId);
    try {
      const res = await getSummary(paperId, refresh);
      setResults((r) => ({ ...r, [paperId]: res.summary }));
    } catch (err) {
      onError(err.message);
    } finally {
      setLoadingId("");
    }
  }

  return (
    <div>
      <h1>Summaries</h1>
      {ready.length === 0 && <p>No processed papers yet. Upload one in My Papers.</p>}

      <div style={{ display: "grid", gap: 16 }}>
        {ready.map((p) => {
          const text = results[p.paper_id] ?? p.summary;
          const busy = loadingId === p.paper_id;
          return (
            <div
              key={p.paper_id}
              style={{
                background: "#fff",
                border: "1px solid #e5e7eb",
                borderRadius: 10,
                padding: 16,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                <strong>{p.filename}</strong>
                <div style={{ display: "flex", gap: 8 }}>
                  <button disabled={busy} onClick={() => summarize(p.paper_id, false)}>
                    {busy ? "Summarizing..." : text ? "Show" : "Summarize"}
                  </button>
                  {text && (
                    <button disabled={busy} onClick={() => summarize(p.paper_id, true)}>
                      Regenerate
                    </button>
                  )}
                </div>
              </div>
              {text && (
                <p style={{ whiteSpace: "pre-wrap", marginBottom: 0 }}>{text}</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}