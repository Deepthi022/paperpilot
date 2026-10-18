import { NavLink } from "react-router-dom";

const links = [
  ["/papers", "📄", "My Papers"],
  ["/chat", "💬", "Chat"],
  ["/compare", "⚖️", "Compare"],
  ["/summaries", "📝", "Summaries"],
  ["/notes", "🗒️", "Notes"],
];

export default function Sidebar({ health }) {
  return (
    <aside className="sidebar">
      <div className="brand">✈️ PaperPilot</div>
      {links.map(([to, icon, label]) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
        >
          <span>{icon}</span>
          {label}
        </NavLink>
      ))}
      <div className="status">
        <span className={`dot${health === "connected" ? " ok" : ""}`} />
        Database: {health}
      </div>
    </aside>
  );
}