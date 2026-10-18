import { useRef, useState } from "react";
import { uploadPaper } from "../services/api";

export default function MyPapers({ papers, reload, onError }) {
  const fileInput = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [drag, setDrag] = useState(false);

  async function upload(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      onError("Only PDF files are allowed");
      return;
    }
    onError("");
    setUploading(true);
    try {
      await uploadPaper(file);
      await reload();
    } catch (err) {
      onError(err.message);
    } finally {
      setUploading(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  function onDrop(e) {
    e.preventDefault();
    setDrag(false);
    if (!uploading) upload(e.dataTransfer.files[0]);
  }

  const badgeClass = (s) => (s === "ready" ? "ready" : s === "failed" ? "failed" : "other");

  return (
    <div>
      <h1>My Papers</h1>

      <div
        className={`dropzone${drag ? " drag" : ""}`}
        onClick={() => !uploading && fileInput.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
      >
        <input
          ref={fileInput}
          type="file"
          accept="application/pdf"
          hidden
          onChange={(e) => upload(e.target.files[0])}
        />
        {uploading ? (
          <>
            <div className="spinner" />
            <strong>Reading and indexing your paper...</strong>
            <span>This takes a few seconds</span>
          </>
        ) : (
          <>
            <div className="drop-icon">📄</div>
            <strong>Drop a PDF here</strong>
            <span>or click to browse</span>
          </>
        )}
      </div>

      <div style={{ marginTop: 24, display: "grid", gap: 12 }}>
        {papers.length === 0 && <p className="meta">No papers yet. Upload a PDF to get started.</p>}
        {papers.map((p) => (
          <div key={p.paper_id} className="paper-card">
            <div className="name">
              <strong>{p.filename}</strong>
              <div className="meta">{p.page_count} pages</div>
            </div>
            <span className={`badge ${badgeClass(p.status)}`}>{p.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}