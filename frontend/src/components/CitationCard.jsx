const BASE = import.meta.env.VITE_API_URL;

export default function CitationCard({ source }) {
  const pdfUrl = `${BASE}/papers/${source.paper_id}/file#page=${source.page}`;
  const pct = Math.max(0, Math.min(100, Math.round(source.score * 100)));

  return (
    <div className="cite-card">
      <div className="cite-top">
        <div>
          <span className="cite">[{source.ref}]</span>{" "}
          <strong>{source.filename}</strong>{" "}
          <span className="cite-pill">page {source.page}</span>
        </div>
        <a href={pdfUrl} target="_blank" rel="noreferrer" style={{ whiteSpace: "nowrap" }}>
          Open page {source.page} ↗
        </a>
      </div>
      <div className="snippet">{source.snippet}...</div>
      <div className="bar" title={`match score ${source.score}`}>
        <div style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}