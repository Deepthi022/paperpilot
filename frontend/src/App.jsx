import { useEffect, useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import MyPapers from "./pages/MyPapers";
import ResearchChat from "./pages/ResearchChat";
import Summaries from "./pages/Summaries";
import ComparePapers from "./pages/ComparePapers";
import Notes from "./pages/Notes";
import { getHealth, getPapers } from "./services/api";

export default function App() {
  const [papers, setPapers] = useState([]);
  const [health, setHealth] = useState("checking...");
  const [error, setError] = useState("");
  const [messages, setMessages] = useState([]); // kept here so chat survives page switches

  const loadPapers = () =>
    getPapers().then(setPapers).catch((e) => setError(e.message));

  useEffect(() => {
    getHealth()
      .then((h) => setHealth(h.database))
      .catch((e) => setError(e.message));
    loadPapers();
  }, []);

  return (
    <div className="app">
      <Sidebar health={health} />
      <main className="main">
        {error && (
          <div className="toast">
            <span>{error}</span>
            <button onClick={() => setError("")}>✕</button>
          </div>
        )}
        <Routes>
          <Route path="/" element={<Navigate to="/papers" replace />} />
          <Route
            path="/papers"
            element={<MyPapers papers={papers} reload={loadPapers} onError={setError} />}
          />
          <Route
            path="/chat"
            element={
              <ResearchChat
                papers={papers}
                messages={messages}
                setMessages={setMessages}
                onError={setError}
              />
            }
          />
          <Route path="/compare" element={<ComparePapers papers={papers} onError={setError} />} />
          <Route path="/summaries" element={<Summaries papers={papers} onError={setError} />} />
          <Route path="/notes" element={<Notes papers={papers} onError={setError} />} />
        </Routes>
      </main>
    </div>
  );
}