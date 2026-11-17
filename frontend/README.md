# PRISM frontend — Evidence, not instinct

React + Vite single-page app for the PRISM backend.

## Run (development)
Start the backend first (port 8000), then:
```bash
npm install
npm run dev        # http://localhost:5173 — /api is proxied to localhost:8000
```

## Build for production
```bash
cp .env.example .env     # set VITE_API_BASE to your deployed backend URL
npm run build            # output in dist/
```
Add your frontend's URL to `CORS_ORIGINS` in the backend `.env`.

## Structure
- `src/App.jsx` — claim form, example claims, state
- `src/api.js` — `POST /api/check`
- `src/components/` — `VerdictCard`, `EvidenceList` (with filters), `SourceStatus`
- `src/styles.css` — dark/light theme
