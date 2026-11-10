# PRISM frontend

Next.js 14 (App Router, TypeScript, plain CSS) UI for PRISM, "SEE BEYOND THE CLAIM."

- `/` landing page: separate header, hero, how-it-works
- `/workspace` verification workspace: sidebar with new check and history, large composer, drag-drop and clipboard image paste, previews with remove, loading and error states, evidence dashboard (verdict, claim, explanation, supporting and contradicting sources with dates, limitations, analysis date)

## Run

```bash
npm install
cp .env.example .env.local     # NEXT_PUBLIC_API_URL must point at the backend
npm run dev                    # http://localhost:3000
```

Start the backend first (see its README). Every figure on screen comes from the API response; the UI invents nothing, and shows the server's error text if a request fails.
