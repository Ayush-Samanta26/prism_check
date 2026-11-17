const LABELS = {
  supported: { text: "Sources support this", cls: "supported" },
  contradicted: { text: "Sources contradict this", cls: "contradicted" },
  mixed: { text: "Sources disagree", cls: "mixed" },
  insufficient: { text: "Not enough evidence", cls: "insufficient" },
};

export default function VerdictCard({ result }) {
  const meta = LABELS[result.verdict] || LABELS.insufficient;
  const pct = Math.round(result.confidence * 100);
  const { supports, contradicts, neutral } = result.counts;

  return (
    <div className={`card verdict ${meta.cls}`}>
      <p className="claim">“{result.claim}”</p>
      <h2>{meta.text}</h2>
      <p>{result.summary}</p>

      <div className="meter" role="img" aria-label={`Evidence strength ${pct} percent`}>
        <div className="fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="meter-label">
        Evidence strength {pct}%{result.cached ? " · cached" : ""}
      </div>

      <div className="tally">
        <span className="t green">{supports} supporting</span>
        <span className="t red">{contradicts} opposing</span>
        <span className="t grey">{neutral} related</span>
      </div>
    </div>
  );
}
