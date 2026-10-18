import { useState } from "react";
import { comparePapers } from "../services/api";

const cell = {
  border: "1px solid #e5e7eb",
  padding: 10,
  verticalAlign: "top",
  fontSize: 14,
};

export default function ComparePapers({ papers, onError }) {
  const [a, setA] = useState("");
  const [b, setB] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const ready = papers.filter((p) => p.status === "ready");

  async function run() {
    onError("");
    setResult(null);
    setLoading(true);
    try {
      setResult(await comparePapers(a, b));
    } catch (err) {
      onError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const options = (
    <>
      <option value="">Select a paper...</option>
      {ready.map((p) => (
        <option key={p.paper_id} value={p.paper_id}>
          {p.filename}
        </option>
      ))}
    </>
  );

  return (
    <div>
      <h1>Compare Papers</h1>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
        <select value={a} onChange={(e) => setA(e.target.value)} style={{ padding: 6 }}>
          {options}
        </select>
        <span>vs</span>
        <select value={b} onChange={(e) => setB(e.target.value)} style={{ padding: 6 }}>
          {options}
        </select>
        <button onClick={run} disabled={!a || !b || a === b || loading}>
          {loading ? "Comparing..." : "Compare"}
        </button>
      </div>
      {a && a === b && <p style={{ color: "#b45309" }}>Choose two different papers.</p>}
      {loading && <p>This can take 10-20 seconds...</p>}

      {result && (
        <div style={{ marginTop: 24 }}>
          <table style={{ borderCollapse: "collapse", width: "100%", background: "#fff" }}>
            <thead>
              <tr>
                <th style={{ ...cell, background: "#f3f4f6", width: 140 }}>Aspect</th>
                <th style={{ ...cell, background: "#f3f4f6" }}>{result.paper_a.filename}</th>
                <th style={{ ...cell, background: "#f3f4f6" }}>{result.paper_b.filename}</th>
              </tr>
            </thead>
            <tbody>
              {result.rows.map((r) => (
                <tr key={r.aspect}>
                  <td style={{ ...cell, fontWeight: 600 }}>{r.aspect}</td>
                  <td style={cell}>{r.paper_a}</td>
                  <td style={cell}>{r.paper_b}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {result.overall && (
            <p style={{ marginTop: 16 }}>
              <strong>Overall:</strong> {result.overall}
            </p>
          )}
        </div>
      )}
    </div>
  );
}