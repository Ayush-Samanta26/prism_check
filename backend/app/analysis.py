"""Transparent, rule-based comparison of a claim against retrieved evidence.

No machine learning is used. Every decision is based on visible signals:
term overlap, negation parity, refutation cue words, number agreement and
a per-source reliability weight. The result is a *signal about what the
retrieved sources say*, not a ruling on truth.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

STOPWORDS = frozenset(
    """a an and are as at be been being but by can could did do does doing for from
    had has have having he her his how i if in into is it its just may might more
    most much must my no nor not of on once only or other our out over own same she
    should so some such than that the their them then there these they this those
    through to too under until up very was we were what when where which while who
    whom why will with would you your about above after again against all am any
    because before below between both down during each few further here off also
    cannot cant isnt doesnt didnt wasnt wont""".split()
)

NEGATORS = frozenset(
    "not no never cannot cant isnt doesnt didnt wasnt wont without neither nor none".split()
)

REFUTE_WORDS = frozenset(
    """myth myths debunked hoax misconception misconceptions false falsely misleading
    disproven refuted untrue unfounded baseless fabricated pseudoscience discredited
    fake incorrect retracted""".split()
)
REFUTE_PHRASES = ("no evidence", "not supported", "no scientific evidence", "lack of evidence")

RELATED_THRESHOLD = 0.34  # minimum relevance for a source to count at all
SENTENCE_THRESHOLD = 0.30  # minimum overlap of best sentence to judge stance


@dataclass
class Evidence:
    source: str
    title: str
    url: str
    text: str
    published: Optional[str] = None
    reliability: float = 0.6
    stance_hint: Optional[str] = None  # "supports" | "contradicts" | "neutral"


@dataclass
class Analyzed:
    evidence: Evidence
    stance: str  # supports | contradicts | neutral | unrelated
    relevance: float
    weight: float
    excerpt: str
    reason: str


# --------------------------------------------------------------------------- text utils
def _stem(word: str) -> str:
    for suffix in ("ingly", "edly", "ing", "ed", "ly", "es", "s"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def tokenize(text: str) -> list[str]:
    raw = re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower())
    return [t.replace("'", "") for t in raw]


def content_terms(text: str) -> list[str]:
    seen: list[str] = []
    for tok in tokenize(text):
        if tok in STOPWORDS or tok.isdigit() or len(tok) < 3:
            continue
        stem = _stem(tok)
        if stem not in seen:
            seen.append(stem)
    return seen


def numbers_in(text: str) -> set[str]:
    return {n.replace(",", "") for n in re.findall(r"\d[\d,]*\.?\d*", text)}


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", text)
    return [p.strip() for p in parts if p.strip()]


def _term_weight(term: str) -> float:
    return 1.5 if len(term) > 6 else 1.0


def _overlap(terms: list[str], text: str) -> float:
    if not terms:
        return 0.0
    stems = {_stem(t) for t in tokenize(text)}
    total = sum(_term_weight(t) for t in terms)
    hit = sum(_term_weight(t) for t in terms if t in stems)
    return hit / total if total else 0.0


def _has_refutation(sentence: str) -> bool:
    low = sentence.lower()
    if any(p in low for p in REFUTE_PHRASES):
        return True
    return any(tok in REFUTE_WORDS for tok in tokenize(low))


def _negation_count(text: str) -> int:
    return sum(1 for tok in tokenize(text) if tok in NEGATORS)


# --------------------------------------------------------------------------- per-source
def analyze_one(claim: str, ev: Evidence) -> Analyzed:
    terms = content_terms(claim)
    claim_nums = numbers_in(claim)
    claim_neg = _negation_count(claim) % 2

    full_text = f"{ev.title}. {ev.text}".strip()
    sentences = split_sentences(full_text) or [full_text]

    best_sentence, best_overlap = "", 0.0
    for s in sentences:
        o = _overlap(terms, s)
        if o > best_overlap:
            best_sentence, best_overlap = s, o

    coverage = _overlap(terms, full_text)
    relevance = round(0.6 * best_overlap + 0.4 * coverage, 3)
    excerpt = (best_sentence or sentences[0])[:320]

    if relevance < RELATED_THRESHOLD:
        return Analyzed(ev, "unrelated", relevance, 0.0, excerpt, "Low overlap with the claim.")

    # Pre-labelled evidence (e.g. a published fact-check rating).
    if ev.stance_hint in ("supports", "contradicts", "neutral"):
        weight = round(relevance * ev.reliability, 3) if ev.stance_hint != "neutral" else 0.0
        return Analyzed(ev, ev.stance_hint, relevance, weight, excerpt, "Rating given by the publisher.")

    if best_overlap < SENTENCE_THRESHOLD:
        return Analyzed(
            ev, "neutral", relevance, 0.0, excerpt,
            "Related topic, but no single passage addresses the claim directly.",
        )

    strength, stance, reason = 1.0, "supports", "Passage covers the claim's key terms without conflict."

    if _has_refutation(best_sentence) and not _has_refutation(claim):
        stance, strength, reason = "contradicts", 1.0, "Passage uses refutation language (e.g. myth, debunked, no evidence)."
    elif (_negation_count(best_sentence) % 2) != claim_neg:
        stance, strength, reason = "contradicts", 0.7, "Passage differs from the claim in negation."
    else:
        sent_nums = numbers_in(best_sentence)
        if claim_nums and sent_nums and not (claim_nums & sent_nums):
            stance, strength, reason = "contradicts", 0.6, "Passage gives different figures than the claim."
        elif claim_nums and claim_nums & sent_nums:
            strength, reason = 1.0, "Passage covers the claim's terms and matches its figures."

    weight = round(relevance * ev.reliability * strength, 3)
    return Analyzed(ev, stance, relevance, weight, excerpt, reason)


# --------------------------------------------------------------------------- aggregate
def assess(claim: str, evidence: list[Evidence]) -> dict:
    analyzed = [analyze_one(claim, e) for e in evidence]
    analyzed.sort(key=lambda a: a.weight, reverse=True)

    support = sum(a.weight for a in analyzed if a.stance == "supports")
    contra = sum(a.weight for a in analyzed if a.stance == "contradicts")
    total = support + contra
    n_support = sum(1 for a in analyzed if a.stance == "supports")
    n_contra = sum(1 for a in analyzed if a.stance == "contradicts")
    n_neutral = sum(1 for a in analyzed if a.stance == "neutral")
    n_unrelated = sum(1 for a in analyzed if a.stance == "unrelated")

    if (n_support + n_contra) < 2 or total < 0.8:
        verdict, confidence = "insufficient", round(min(total / 0.8, 1.0) * 0.4, 2)
    else:
        ratio = support / total
        if ratio >= 0.75:
            verdict = "supported"
        elif ratio <= 0.25:
            verdict = "contradicted"
        else:
            verdict = "mixed"
        agreement = abs(ratio - 0.5) * 2 if verdict != "mixed" else 1 - abs(ratio - 0.5) * 2
        volume = min(total / 3.0, 1.0)
        confidence = round(max(0.1, min(0.95, 0.5 * agreement + 0.5 * volume)), 2)

    summary = _summary(verdict, n_support, n_contra, n_neutral)
    return {
        "verdict": verdict,
        "confidence": confidence,
        "summary": summary,
        "counts": {
            "supports": n_support,
            "contradicts": n_contra,
            "neutral": n_neutral,
            "unrelated": n_unrelated,
        },
        "support_weight": round(support, 3),
        "contradict_weight": round(contra, 3),
        "analyzed": analyzed,
    }


def _summary(verdict: str, ns: int, nc: int, nn: int) -> str:
    if verdict == "supported":
        return f"{ns} retrieved source(s) back this claim and {nc} push against it."
    if verdict == "contradicted":
        return f"{nc} retrieved source(s) push against this claim and {ns} back it."
    if verdict == "mixed":
        return f"Sources disagree: {ns} lean towards the claim, {nc} lean against it."
    return (
        "Not enough relevant evidence was found to say either way "
        f"({ns} supporting, {nc} opposing, {nn} only loosely related)."
    )
