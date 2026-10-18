import { useEffect, useRef, useState } from "react";
import { askQuestion } from "../services/api";
import CitationCard from "../components/CitationCard";

const SUGGESTIONS = [
  "What is the main research question?",
  "What methodology was used?",
  "What are the key findings?",
  "What are the limitations of this study?",
];

// Turns **bold**, * bullets and [1] citations into nicer output
function renderAnswer(text) {
  const clean = text.replace(/^\* /gm, "• ");
  return clean.split(/(\*\*[^*]+\*\*|\[\d+\])/g).map((part, i) => {
    if (/^\*\*[^*]+\*\*$/.test(part)) return <strong key={i}>{part.slice(2, -2)}</strong>;
    if (/^\[\d+\]$/.test(part)) return <span key={i} className="cite">{part}</span>;
    return part;
  });
}

export default function ResearchChat({ papers, messages, setMessages, onError }) {
  const [selected, setSelected] = useState("");
  const [question, setQuestion] = useState("");
  const [pending, setPending] = useState("");
  const endRef = useRef(null);

  const ready = papers.filter((p) => p.status === "ready");

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pending]);

  async function ask(text) {
    const q = text.trim();
    if (!q || pending) return;
    onError("");
    setPending(q);
    setQuestion("");
    try {
      const res = await askQuestion(q, selected);
      setMessages((m) => [...m, { question: q, answer: res.answer, sources: res.sources }]);
    } catch (err) {
      onError(err.message);
    } finally {
      setPending("");
    }
  }

  return (
    <div className="chat">
      <div className="chat-header">
        <h1>Chat</h1>
        <select value={selected} onChange={(e) => setSelected(e.target.value)}>
          <option value="">All papers</option>
          {ready.map((p) => (
            <option key={p.paper_id} value={p.paper_id}>{p.filename}</option>
          ))}
        </select>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && !pending && (
          <div className="empty">
            <div className="big">💬</div>
            <p>Ask anything about your papers. Every answer comes with sources.</p>
            <div className="chips">
              {SUGGESTIONS.map((s) => (
                <button key={s} className="chip" onClick={() => ask(s)}>{s}</button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} style={{ display: "grid", gap: 10 }}>
            <div className="row user"><div className="bubble user">{m.question}</div></div>
            <div className="row">
              <div style={{ maxWidth: "85%" }}>
                <div className="bubble bot" style={{ maxWidth: "100%" }}>{renderAnswer(m.answer)}</div>
                <details>
                  <summary>Sources ({m.sources.length})</summary>
                  {m.sources.map((s) => <CitationCard key={s.ref} source={s} />)}
                </details>
              </div>
            </div>
          </div>
        ))}

        {pending && (
          <div style={{ display: "grid", gap: 10 }}>
            <div className="row user"><div className="bubble user">{pending}</div></div>
            <div className="row">
              <div className="bubble bot">
                <div className="typing"><span /><span /><span /></div>
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form
        className="chat-input"
        onSubmit={(e) => { e.preventDefault(); ask(question); }}
      >
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about your papers..."
          disabled={!!pending}
        />
        <button type="submit" disabled={!!pending || !question.trim()}>
          {pending ? "Thinking..." : "Ask"}
        </button>
      </form>
    </div>
  );
}