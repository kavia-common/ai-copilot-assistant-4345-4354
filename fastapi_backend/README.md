# FastAPI Backend for AI Copilot (Google Gemini)

This is the backend API server for the AI Copilot application. It exposes REST endpoints for health checks and asking questions, and integrates with Google Gemini.

## Endpoints
- GET / -> Health check (JSON like {"status":"ok"})
- GET /api/health -> Health check (200 JSON indicating service is up)
- POST /api/ask -> Body: { "question": "string" } returns { "answer": "...", "model": "..." }

## Environment
- GOOGLE_GEMINI_API_KEY: required for real responses. Without it, /api/ask returns a 400 error with guidance.
- GEMINI_MODEL: default "gemini-1.5-pro"
- FRONTEND_ORIGIN: optional, default "http://localhost:3000" (added to CORS allowlist if set)
- BACKEND_PORT: default 3001

Create a local environment file by copying `.env.example` to `.env` and filling in your values as needed. Never expose GOOGLE_GEMINI_API_KEY to the frontend.

## CORS
For local development, CORS is configured to allow:
- http://localhost:3000
- http://127.0.0.1:3000
If you set FRONTEND_ORIGIN, it is also allowed automatically. The middleware allows all methods and headers and enables credentials.

## Run locally
- Install dependencies:
  pip install -r requirements.txt
- Start on the default port (3001):
  uvicorn src.api.main:app --host 0.0.0.0 --port ${BACKEND_PORT:-3001}
- Visit API docs:
  http://localhost:3001/docs

## End-to-end run instructions
- Backend:
  - Set GOOGLE_GEMINI_API_KEY in `fastapi_backend/.env`. Optionally set GEMINI_MODEL.
  - Start the backend on port 3001.
- Frontend:
  - Ensure REACT_APP_API_BASE is http://localhost:3001 (default).
  - Start the frontend on port 3000.
- Test health:
  - GET http://localhost:3001/api/health should return {"ok": true}.
- Test ask:
  - POST http://localhost:3001/api/ask with {"question":"Hello"} should return {"answer":"...", "model":"..."}.

## Troubleshooting
- 400 Bad Request:
  - Empty question or missing GOOGLE_GEMINI_API_KEY. Add the key and restart.
- 502 Bad Gateway:
  - Upstream provider/network errors. Verify model, key, quota, network.
- CORS errors:
  - Ensure frontend runs on http://localhost:3000 or http://127.0.0.1:3000.
  - If using a different origin, set FRONTEND_ORIGIN in backend .env and restart.
- Connection issues from frontend:
  - Confirm REACT_APP_API_BASE matches backend URL (http://localhost:3001).
  - Restart the React dev server after changing env.

## Logs
Server logs appear in the terminal where you run uvicorn. /api/ask logs prompt length and snippets. Exceptions are logged with stack traces when appropriate.

## Data and Persistence
No database included. Interactions are stateless: the frontend sends a question, backend calls Gemini, returns an answer.
