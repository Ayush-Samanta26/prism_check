"""Live public evidence sources. Each fetcher returns a list[Evidence]."""
from __future__ import annotations

import asyncio
import html
import os
import re
import xml.etree.ElementTree as ET

import httpx

from .analysis import Evidence, content_terms

USER_AGENT = "PRISM-FactCheck/1.0 (educational project; contact: set-your-email@example.com)"
TIMEOUT = httpx.Timeout(12.0, connect=6.0)


def build_query(claim: str, max_terms: int = 8) -> str:
    terms = content_terms(claim)
    return " ".join(terms[:max_terms]) or claim


def _strip_tags(text: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text or ""))).strip()


# --------------------------------------------------------------------------- Wikipedia
async def fetch_wikipedia(client: httpx.AsyncClient, claim: str) -> list[Evidence]:
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": build_query(claim),
        "gsrlimit": 5,
        "prop": "extracts|info",
        "exintro": 1,
        "explaintext": 1,
        "exsentences": 8,
        "exlimit": 5,
        "inprop": "url",
    }
    r = await client.get("https://en.wikipedia.org/w/api.php", params=params)
    r.raise_for_status()
    pages = (r.json().get("query") or {}).get("pages") or {}
    out = []
    for page in sorted(pages.values(), key=lambda p: p.get("index", 99)):
        text = page.get("extract") or ""
        if not text:
            continue
        out.append(
            Evidence(
                source="Wikipedia",
                title=page.get("title", ""),
                url=page.get("fullurl", ""),
                text=text,
                published=(page.get("touched") or "")[:10] or None,
                reliability=0.6,
            )
        )
    return out


# --------------------------------------------------------------------------- Crossref
async def fetch_crossref(client: httpx.AsyncClient, claim: str) -> list[Evidence]:
    params = {
        "query": build_query(claim),
        "rows": 6,
        "select": "title,abstract,DOI,URL,container-title,issued",
    }
    r = await client.get("https://api.crossref.org/works", params=params)
    r.raise_for_status()
    items = (r.json().get("message") or {}).get("items") or []
    out = []
    for it in items:
        title = (it.get("title") or [""])[0]
        abstract = _strip_tags(it.get("abstract", ""))
        if not title:
            continue
        year = None
        parts = (it.get("issued") or {}).get("date-parts") or [[None]]
        if parts and parts[0] and parts[0][0]:
            year = str(parts[0][0])
        journal = (it.get("container-title") or [""])[0]
        out.append(
            Evidence(
                source="Crossref" + (f" · {journal}" if journal else ""),
                title=title,
                url=it.get("URL") or f"https://doi.org/{it.get('DOI', '')}",
                text=abstract or title,
                published=year,
                reliability=0.7 if abstract else 0.4,
            )
        )
    return out


# --------------------------------------------------------------------------- PubMed
async def fetch_pubmed(client: httpx.AsyncClient, claim: str) -> list[Evidence]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    r = await client.get(
        f"{base}/esearch.fcgi",
        params={"db": "pubmed", "term": build_query(claim), "retmax": 5, "retmode": "json", "sort": "relevance"},
    )
    r.raise_for_status()
    ids = (r.json().get("esearchresult") or {}).get("idlist") or []
    if not ids:
        return []
    r = await client.get(
        f"{base}/efetch.fcgi",
        params={"db": "pubmed", "id": ",".join(ids), "retmode": "xml", "rettype": "abstract"},
    )
    r.raise_for_status()
    root = ET.fromstring(r.text)
    out = []
    for art in root.findall(".//PubmedArticle"):
        pmid = (art.findtext(".//PMID") or "").strip()
        title = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
        abstract = " ".join("".join(n.itertext()) for n in art.findall(".//Abstract/AbstractText"))
        if not abstract:
            continue
        year = art.findtext(".//JournalIssue/PubDate/Year") or None
        journal = art.findtext(".//Journal/Title") or ""
        out.append(
            Evidence(
                source="PubMed" + (f" · {journal}" if journal else ""),
                title=title,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                text=abstract,
                published=year,
                reliability=0.9,
            )
        )
    return out


# --------------------------------------------------------------------------- Google Fact Check (optional)
def _rating_to_stance(rating: str) -> str:
    r = rating.lower()
    if any(w in r for w in ("half", "mixture", "partly", "partially", "unproven", "needs context")):
        return "neutral"
    if any(w in r for w in ("false", "incorrect", "misleading", "fake", "hoax", "wrong", "fabricated", "pants")):
        return "contradicts"
    if any(w in r for w in ("true", "correct", "accurate", "right")):
        return "supports"
    return "neutral"


async def fetch_factcheck(client: httpx.AsyncClient, claim: str) -> list[Evidence]:
    key = os.getenv("GOOGLE_FACTCHECK_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Skipped: GOOGLE_FACTCHECK_API_KEY not set")
    r = await client.get(
        "https://factchecktools.googleapis.com/v1alpha1/claims:search",
        params={"query": claim[:200], "pageSize": 5, "languageCode": "en", "key": key},
    )
    r.raise_for_status()
    out = []
    for c in r.json().get("claims", []):
        for rev in c.get("claimReview", [])[:1]:
            rating = rev.get("textualRating", "")
            out.append(
                Evidence(
                    source=f"Fact-check · {(rev.get('publisher') or {}).get('name', 'publisher')}",
                    title=rev.get("title") or c.get("text", ""),
                    url=rev.get("url", ""),
                    text=f"{c.get('text', '')}. Rated: {rating}.",
                    published=(rev.get("reviewDate") or "")[:10] or None,
                    reliability=0.9,
                    stance_hint=_rating_to_stance(rating),
                )
            )
    return out


SOURCES = {
    "Wikipedia": fetch_wikipedia,
    "Crossref": fetch_crossref,
    "PubMed": fetch_pubmed,
    "Google Fact Check": fetch_factcheck,
}


async def gather_evidence(claim: str) -> tuple[list[Evidence], list[dict]]:
    async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
        names = list(SOURCES)
        results = await asyncio.gather(*(SOURCES[n](client, claim) for n in names), return_exceptions=True)
    evidence: list[Evidence] = []
    status: list[dict] = []
    for name, res in zip(names, results):
        if isinstance(res, Exception):
            msg = str(res) or res.__class__.__name__
            status.append({"name": name, "ok": False, "count": 0, "error": msg[:160]})
        else:
            evidence.extend(res)
            status.append({"name": name, "ok": True, "count": len(res), "error": None})
    return evidence, status
