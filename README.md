# AI Copilot - Backend Workspace (FastAPI + Google Gemini)

This workspace contains the FastAPI backend for the AI Copilot application. The paired React frontend lives in a separate workspace (`ai-copilot-assistant-4345-4355`).

## Endpoints
- GET / and GET /api/health
- POST /api/ask with body { "question": "string" }

## Configuration (Environment)
Create `ai-copilot-assistant-4345-4354/fastapi_backend/.env` with:
- GOOGLE_GEMINI_API_KEY: required for real responses.
- GEMINI_MODEL: optional, default "gemini-1.5-pro".
- FRONTEND_ORIGIN: optional, e.g. http://localhost:3000 (added to CORS allowlist).
- BACKEND_PORT: optional, default 3001.

Example .env:
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-pro
FRONTEND_ORIGIN=http://localhost:3000
BACKEND_PORT=3001

Never expose GOOGLE_GEMINI_API_KEY to the frontend.

## CORS
Allowed by default:
- http://localhost:3000
- http://127.0.0.1:3000
If FRONTEND_ORIGIN is set, it is also allowed automatically.

## Run locally (Backend)
- Install dependencies:
  pip install -r ai-copilot-assistant-4345-4354/fastapi_backend/requirements.txt
- Start the server on port 3001:
  uvicorn fastapi_backend.src.api.main:app --host 0.0.0.0 --port 3001
- Open API docs:
  http://localhost:3001/docs

## End-to-end (Backend + Frontend)
Frontend lives in `ai-copilot-assistant-4345-4355/react_frontend`.

1) Backend:
   - Ensure .env has GOOGLE_GEMINI_API_KEY.
   - Start backend on port 3001.

2) Frontend:
   - Ensure environment REACT_APP_API_BASE points to http://localhost:3001 (default already).
   - Start frontend on port 3000.

3) Test:
   - Health: GET http://localhost:3001/api/health (should return { "ok": true }).
   - From frontend UI, ask a question. This will POST to http://localhost:3001/api/ask.

Curl examples:
- Health:
  curl -s http://localhost:3001/api/health
- Ask:
  curl -s -X POST http://localhost:3001/api/ask -H "Content-Type: application/json" -d '{"question":"Hello, who are you?"}'

## Troubleshooting
- 400 "Question must not be empty": Provide a non-empty question.
- 400 "Configuration error" with hint to set GOOGLE_GEMINI_API_KEY: Add the key to backend .env and restart.
- 502 "Upstream AI provider error": Check model name, API key validity, provider status, and network.
- CORS errors in browser:
  - Ensure frontend is on http://localhost:3000 or http://127.0.0.1:3000.
  - If using a different origin, set FRONTEND_ORIGIN in backend .env and restart.
- Connection errors:
  - Verify REACT_APP_API_BASE (frontend) matches backend origin/port.
  - Confirm backend listening on port 3001 and reachable from the browser.

No OpenAI usage remains; the backend integrates with Google Gemini exclusively.
