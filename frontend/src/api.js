const BASE = import.meta.env.VITE_API_BASE || "";

export async function checkClaim(claim, signal) {
  const res = await fetch(`${BASE}/api/check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ claim }),
    signal,
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
      else if (Array.isArray(body.detail)) detail = body.detail.map((d) => d.msg).join("; ");
    } catch {
      /* keep default message */
    }
    throw new Error(detail);
  }
  return res.json();
}
