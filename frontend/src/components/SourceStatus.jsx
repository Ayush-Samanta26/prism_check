export default function SourceStatus({ status }) {
  return (
    <div className="card sources">
      <h3>Sources queried</h3>
      <ul>
        {status.map((s) => (
          <li key={s.name} className={s.ok ? "ok" : "fail"} title={s.error || ""}>
            <span className="dot" />
            <strong>{s.name}</strong>
            <span className="muted">
              {s.ok ? `${s.count} passage${s.count === 1 ? "" : "s"}` : s.error || "unavailable"}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
