# PRISM backend — Evidence, not instinct

FastAPI service that takes a claim, pulls live passages from public sources and shows what they support.

## Sources
- Wikipedia (no key)
- Crossref scholarly metadata/abstracts (no key)
- PubMed abstracts via NCBI E-utilities (no key)
- Google Fact Check Tools (optional, set `GOOGLE_FACTCHECK_API_KEY`)

## Run
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # optional
uvicorn app.main:app --reload --port 8000
```
Docs: http://localhost:8000/docs

Edit `USER_AGENT` in `app/sources.py` to include your contact email (Wikipedia/NCBI ask for this).

## API
`POST /api/check` with `{"claim": "..."}` returns verdict (`supported | contradicted | mixed | insufficient`),
confidence, per-source evidence with stance, and source status. `GET /api/health` lists sources.

## How the verdict works
`app/analysis.py` — no ML. For each passage: term overlap with the claim, negation parity,
refutation words (myth, debunked, no evidence…), number agreement, weighted by source reliability.
Weights are summed for/against. Fewer than 2 relevant passages → `insufficient`.
This is a heuristic signal about retrieved text, not proof of truth. Subtle claims, sarcasm and
context will fool it, so always read the linked sources.

## Tests
```bash
python -m unittest discover -s tests -v
```

## Docker
```bash
docker build -t prism-backend . && docker run -p 8000:8000 prism-backend
```
