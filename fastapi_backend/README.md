# FastAPI Backend for AI Copilot

This is the backend API server for the AI Copilot application. It exposes REST endpoints for health checks and asking questions, and integrates with Google Gemini.

## Endpoints
- GET / -> Health check (JSON like {"status":"ok"})
- GET /api/health -> Health check (200 JSON indicating service is up)
- POST /api/ask -> Body: { "question": "string" } returns { "answer": "...", "model": "..." }

## Environment
- GOOGLE_GEMINI_API_KEY: required for real responses. Without it, /api/ask returns a 400 error with guidance.
- GEMINI_MODEL: default gemini-1.5-pro
- FRONTEND_ORIGIN: default http://localhost:3000
- BACKEND_PORT: default 3001

Create a local environment file by copying `.env.example` to `.env` and filling in your values as needed. Never expose GOOGLE_GEMINI_API_KEY to the frontend.

## CORS
For local development, CORS is configured to allow:
- http://localhost:3000
- http://127.0.0.1:3000
You can also set FRONTEND_ORIGIN to match your frontend origin. The middleware is configured with allow_methods and allow_headers set to "*", and credentials are enabled by default in code. If you change origins, restart the server.

## Run locally
- Install dependencies:
  pip install -r requirements.txt
- Start on the default port (3001):
  uvicorn src.api.main:app --host 0.0.0.0 --port ${BACKEND_PORT:-3001}
- Switch to port 8000 if preferred:
  uvicorn src.api.main:app --host 0.0.0.0 --port 8000
- Visit API docs:
  http://localhost:3001/docs (or http://localhost:8000/docs)

## Health checks and verification
- Health: GET http://localhost:3001/api/health should return a small JSON confirming the service is up. The root path / also returns a simple health JSON.
- End-to-end: After starting the frontend at http://localhost:3000, submit a question from the UI. The frontend posts to ${REACT_APP_API_BASE}/api/ask and displays the answer or an informative error.

## Error mapping
- 400 Bad Request: empty question or configuration issues (e.g., missing GOOGLE_GEMINI_API_KEY) with a clear message and action hint.
- 502 Bad Gateway: upstream provider/network errors with hints to check model, key, quota, or connectivity.
- 500 Internal Server Error: unexpected exceptions.

## Logs
- Server logs appear in the terminal where you run uvicorn. Requests to /api/ask log the prompt length and snippets. Exceptions are logged with stack traces when appropriate.

## Data and Persistence
This backend does not include or require any database or persistence layer in the current scope. All AI interactions are stateless: the frontend sends the user’s question to this FastAPI service, which forwards the request to the configured AI provider and returns the answer in a single request-response cycle. No chat history, user accounts, or other data are stored by the backend.

If future features require persistence (such as chat history, user profiles, or rate limiting), they will need:
- A separate database to be provisioned and configured, and
- Corresponding backend changes to manage data models, migrations, and storage access.

Until such changes are implemented, deployments should not expect or configure any database for this service.
