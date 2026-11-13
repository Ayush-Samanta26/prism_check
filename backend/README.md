# PRISM backend

FastAPI service behind PRISM, the claim-verification workspace ("SEE BEYOND THE CLAIM").

## Pipeline

1. **OCR** each uploaded screenshot (Tesseract; English, Hindi, Bengali by default).
2. **Claim extraction** with Claude (vision): finds the one checkable claim and writes search queries.
3. **Web search** (Tavily or Brave) across those queries, de-duplicated into at most 8 sources.
4. **Evidence judgement** with Claude: verdict, confidence, explanation, supporting and contradicting sources, limitations.
5. **Guards** (`app/services/normalize.py`): citations can only point at sources search actually returned; a definite verdict with no cited evidence, or with no sources at all, is downgraded to `UNVERIFIABLE`.

If the LLM key, search key or a provider call fails, the API returns an error. It never invents a result.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add ANTHROPIC_API_KEY and TAVILY_API_KEY (or BRAVE_API_KEY)
sudo apt install tesseract-ocr tesseract-ocr-hin tesseract-ocr-ben   # optional but recommended
uvicorn app.main:app --reload --port 8000
```

Docs at http://localhost:8000/docs. Check `GET /api/health` to see which services are configured.

## With Postgres

`docker compose up --build` starts Postgres and the API (reads keys from `.env`).

## API

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Config status (no secrets) |
| POST | `/api/verify` | multipart: `text`, optional `chat_id`, `files` (up to 4 images) |
| GET | `/api/chats` | History list |
| GET | `/api/chats/{id}` | Messages with stored reports |
| DELETE | `/api/chats/{id}` | Delete a chat |

## Tests

```bash
pytest
```

Covers the verdict and citation guards. Live LLM and search calls are not mocked or faked in this repo.

## Not included yet

Redis/Celery background jobs, auth and per-user history. History is global to the deployment for now.
