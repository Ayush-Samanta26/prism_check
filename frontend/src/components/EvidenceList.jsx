import { useState } from "react";

const FILTERS = [
  ["all", "All"],
  ["supports", "Supporting"],
  ["contradicts", "Opposing"],
  ["neutral", "Related"],
];
const STANCE_TEXT = {
  supports: "Supports",
  contradicts: "Opposes",
  neutral: "Related",
  unrelated: "Unrelated",
};

export default function EvidenceList({ evidence }) {
  const [filter, setFilter] = useState("all");
  const shown = evidence.filter((e) => filter === "all" || e.stance === filter);

  return (
    <div className="card">
      <div className="list-head">
        <h3>Evidence ({evidence.length})</h3>
        <div className="tabs" role="tablist">
          {FILTERS.map(([key, label]) => (
            <button
              key={key}
              role="tab"
              aria-selected={filter === key}
              className={filter === key ? "tab active" : "tab"}
              onClick={() => setFilter(key)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {shown.length === 0 && <p className="muted">Nothing in this category.</p>}

      <ul className="evidence">
        {shown.map((e, i) => (
          <li key={`${e.url}-${i}`} className={`ev ${e.stance}`}>
            <div className="ev-top">
              <span className={`badge ${e.stance}`}>{STANCE_TEXT[e.stance] || e.stance}</span>
              <span className="src">{e.source}{e.published ? ` · ${e.published}` : ""}</span>
            </div>
            <a href={e.url} target="_blank" rel="noopener noreferrer" className="ev-title">
              {e.title}
            </a>
            <p className="excerpt">{e.excerpt}</p>
            <p className="reason">
              {e.reason} · relevance {Math.round(e.relevance * 100)}%
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
