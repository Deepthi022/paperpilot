const BASE = import.meta.env.VITE_API_URL;

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json();
}

const json = (method, body) => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export const getHealth = () => request("/health");
export const getPapers = () => request("/papers");

export async function uploadPaper(file) {
  const form = new FormData();
  form.append("file", file);
  return request("/papers", { method: "POST", body: form });
}

export const askQuestion = (question, paperId) =>
  request("/chat", json("POST", {
    question,
    paper_ids: paperId ? [paperId] : null,
    top_k: 5,
  }));

export const getSummary = (paperId, refresh = false) =>
  request(`/summaries/${paperId}?refresh=${refresh}`, { method: "POST" });

export const comparePapers = (idA, idB) =>
  request("/compare", json("POST", { paper_ids: [idA, idB] }));

export const getNotes = (paperId) => request(`/notes?paper_id=${paperId}`);
export const createNote = (paperId, text) =>
  request("/notes", json("POST", { paper_id: paperId, text }));
export const updateNote = (noteId, text) =>
  request(`/notes/${noteId}`, json("PUT", { text }));
export const deleteNote = (noteId) =>
  request(`/notes/${noteId}`, { method: "DELETE" });