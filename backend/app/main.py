"""PRISM API — compares a claim with live public evidence."""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .analysis import assess
from .sources import SOURCES, gather_evidence

CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "600"))
_cache: dict[str, tuple[float, dict]] = {}

METHOD_NOTE = (
    "PRISM retrieves passages from public sources and compares them with your claim using "
    "transparent rules (term overlap, negation, refutation wording, figures, source weight). "
    "It shows what the retrieved sources appear to say; it does not prove a claim true or false. "
    "Always open the linked sources."
)

app = FastAPI(title="PRISM", version="1.0.0", description="Evidence, not instinct.")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class CheckRequest(BaseModel):
    claim: str = Field(..., min_length=8, max_length=500)


class EvidenceOut(BaseModel):
    source: str
    title: str
    url: str
    excerpt: str
    published: str | None
    stance: str
    relevance: float
    weight: float
    reason: str


class SourceStatus(BaseModel):
    name: str
    ok: bool
    count: int
    error: str | None


class CheckResponse(BaseModel):
    claim: str
    verdict: str
    confidence: float
    summary: str
    counts: dict[str, int]
    evidence: list[EvidenceOut]
    source_status: list[SourceStatus]
    method_note: str
    checked_at: str
    cached: bool = False


@app.get("/api/health")
def health():
    return {"status": "ok", "sources": list(SOURCES)}


@app.post("/api/check", response_model=CheckResponse)
async def check(req: CheckRequest):
    claim = " ".join(req.claim.split())
    key = claim.lower()

    hit = _cache.get(key)
    if hit and time.time() - hit[0] < CACHE_TTL:
        return {**hit[1], "cached": True}

    evidence, status = await gather_evidence(claim)
    if not any(s["ok"] for s in status):
        raise HTTPException(status_code=502, detail="Could not reach any evidence source. Try again shortly.")

    result = assess(claim, evidence)
    shown = [a for a in result["analyzed"] if a.stance != "unrelated"] or result["analyzed"][:5]
    payload = {
        "claim": claim,
        "verdict": result["verdict"],
        "confidence": result["confidence"],
        "summary": result["summary"],
        "counts": result["counts"],
        "evidence": [
            {
                "source": a.evidence.source,
                "title": a.evidence.title,
                "url": a.evidence.url,
                "excerpt": a.excerpt,
                "published": a.evidence.published,
                "stance": a.stance,
                "relevance": a.relevance,
                "weight": a.weight,
                "reason": a.reason,
            }
            for a in shown
        ],
        "source_status": status,
        "method_note": METHOD_NOTE,
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cached": False,
    }
    _cache[key] = (time.time(), payload)
    return payload
