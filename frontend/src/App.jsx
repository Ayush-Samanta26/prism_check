import { useRef, useState } from "react";
import { checkClaim } from "./api.js";
import VerdictCard from "./components/VerdictCard.jsx";
import EvidenceList from "./components/EvidenceList.jsx";
import SourceStatus from "./components/SourceStatus.jsx";

const EXAMPLES = [
  "Humans only use 10 percent of their brains",
  "Water boils at 100 degrees Celsius at sea level",
  "The Great Wall of China is visible from space",
  "Vaccines cause autism in children",
];

export default function App() {
  const [claim, setClaim] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const abortRef = useRef(null);

  async function run(text) {
    const value = (text ?? claim).trim();
    if (value.length < 8) {
      setError("Please enter a claim of at least 8 characters.");
      return;
    }
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      setResult(await checkClaim(value, controller.signal));
    } catch (e) {
      if (e.name !== "AbortError") setError(e.message || "Something went wrong.");
    } finally {
      if (abortRef.current === controller) setLoading(false);
    }
  }

  function onSubmit(e) {
    e.preventDefault();
    run();
  }

  return (
    <div className="page">
      <header className="hero">
        <div className="logo" aria-hidden="true">
          <svg viewBox="0 0 48 48" width="40" height="40">
            <polygon points="24,5 43,38 5,38" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" />
            <line x1="2" y1="26" x2="19" y2="25" stroke="currentColor" strokeWidth="2" />
            <line x1="27" y1="23" x2="46" y2="14" stroke="#e5484d" strokeWidth="2" />
            <line x1="27" y1="25" x2="46" y2="25" stroke="#f5a524" strokeWidth="2" />
            <line x1="27" y1="27" x2="46" y2="36" stroke="#30a46c" strokeWidth="2" />
          </svg>
        </div>
        <h1>PRISM</h1>
        <p className="tagline">Evidence, not instinct.</p>
        <p className="sub">
          Paste a claim. PRISM pulls live public sources and shows what they can — and can't — support.
        </p>
      </header>

      <main>
        <form className="check" onSubmit={onSubmit}>
          <label htmlFor="claim" className="sr-only">Claim to check</label>
          <textarea
            id="claim"
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
            placeholder="e.g. Humans only use 10 percent of their brains"
            maxLength={500}
            rows={3}
          />
          <div className="row">
            <span className="count">{claim.length}/500</span>
            <button type="submit" disabled={loading}>
              {loading ? "Checking sources…" : "Check claim"}
            </button>
          </div>
        </form>

        <div className="examples">
          <span>Try:</span>
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              className="chip"
              disabled={loading}
              onClick={() => {
                setClaim(ex);
                run(ex);
              }}
            >
              {ex}
            </button>
          ))}
        </div>

        {error && <div className="error" role="alert">{error}</div>}

        {loading && (
          <div className="loading" aria-live="polite">
            <div className="spinner" /> Searching Wikipedia, Crossref, PubMed…
          </div>
        )}

        {result && (
          <section className="results" aria-live="polite">
            <VerdictCard result={result} />
            <EvidenceList evidence={result.evidence} />
            <SourceStatus status={result.source_status} />
            <p className="note">{result.method_note}</p>
          </section>
        )}
      </main>

      <footer>
        PRISM is an educational tool. Verdicts are heuristic signals from retrieved text, not final judgments.
      </footer>
    </div>
  );
}
