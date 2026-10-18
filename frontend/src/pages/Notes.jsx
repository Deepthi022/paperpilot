import { useEffect, useState } from "react";
import { getNotes, createNote, updateNote, deleteNote } from "../services/api";

export default function Notes({ papers, onError }) {
  const [paperId, setPaperId] = useState("");
  const [notes, setNotes] = useState([]);
  const [text, setText] = useState("");
  const [editingId, setEditingId] = useState("");
  const [editText, setEditText] = useState("");

  const ready = papers.filter((p) => p.status === "ready");

  async function load(id) {
    if (!id) return setNotes([]);
    try {
      setNotes(await getNotes(id));
    } catch (err) {
      onError(err.message);
    }
  }

  useEffect(() => {
    load(paperId);
  }, [paperId]);

  async function add(e) {
    e.preventDefault();
    if (!text.trim()) return;
    onError("");
    try {
      await createNote(paperId, text);
      setText("");
      await load(paperId);
    } catch (err) {
      onError(err.message);
    }
  }

  async function saveEdit(id) {
    if (!editText.trim()) return;
    onError("");
    try {
      await updateNote(id, editText);
      setEditingId("");
      await load(paperId);
    } catch (err) {
      onError(err.message);
    }
  }

  async function remove(id) {
    if (!window.confirm("Delete this note?")) return;
    onError("");
    try {
      await deleteNote(id);
      await load(paperId);
    } catch (err) {
      onError(err.message);
    }
  }

  return (
    <div>
      <h1>Notes</h1>
      <select
        value={paperId}
        onChange={(e) => setPaperId(e.target.value)}
        style={{ padding: 6 }}
      >
        <option value="">Select a paper...</option>
        {ready.map((p) => (
          <option key={p.paper_id} value={p.paper_id}>
            {p.filename}
          </option>
        ))}
      </select>

      {paperId && (
        <>
          <form onSubmit={add} style={{ marginTop: 16, display: "grid", gap: 8 }}>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Write a note about this paper..."
              rows={3}
              style={{ padding: 8, fontFamily: "inherit" }}
            />
            <div>
              <button type="submit" disabled={!text.trim()}>
                Save note
              </button>
            </div>
          </form>

          <div style={{ marginTop: 20, display: "grid", gap: 12 }}>
            {notes.length === 0 && <p>No notes for this paper yet.</p>}
            {notes.map((n) => (
              <div
                key={n.note_id}
                style={{
                  background: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: 10,
                  padding: 14,
                }}
              >
                {editingId === n.note_id ? (
                  <>
                    <textarea
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                      rows={3}
                      style={{ width: "100%", padding: 8, fontFamily: "inherit" }}
                    />
                    <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                      <button onClick={() => saveEdit(n.note_id)}>Save</button>
                      <button onClick={() => setEditingId("")}>Cancel</button>
                    </div>
                  </>
                ) : (
                  <>
                    <p style={{ whiteSpace: "pre-wrap", margin: "0 0 8px" }}>{n.text}</p>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      <small style={{ color: "#6b7280", marginRight: "auto" }}>
                        {new Date(n.updated_at + "Z").toLocaleString()}
                      </small>
                      <button
                        onClick={() => {
                          setEditingId(n.note_id);
                          setEditText(n.text);
                        }}
                      >
                        Edit
                      </button>
                      <button onClick={() => remove(n.note_id)}>Delete</button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}