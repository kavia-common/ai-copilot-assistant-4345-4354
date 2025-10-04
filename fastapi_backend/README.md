# FastAPI Backend for AI Copilot

This is the backend API server for the AI Copilot application. It exposes REST endpoints for health checks and asking questions, and integrates with the OpenAI API.

## Endpoints
- GET / -> Health check
- GET /api/health -> Health check (200 JSON: {"status":"ok"})
- POST /api/ask -> Body: { "question": "string" }

## Environment
- OPENAI_API_KEY: required for real responses (without it, /api/ask returns a 400-friendly error message)
- OPENAI_BASE_URL: default https://api.openai.com/v1
- OPENAI_MODEL: default gpt-4o-mini
- FRONTEND_ORIGIN: default http://localhost:3000
- BACKEND_PORT: default 3001

Create a local environment file by copying `.env.example` to `.env` and filling in your values as needed.

## CORS
For local development, CORS is configured to allow:
- http://localhost:3000
- http://127.0.0.1:3000
- FRONTEND_ORIGIN (if provided)

Credentials are disabled (allow_credentials: false) to avoid preflight/cookie constraints during local development.

## Run locally
- Install dependencies: `pip install -r requirements.txt`
- Start: `uvicorn src.api.main:app --host 0.0.0.0 --port ${BACKEND_PORT:-3001}`
- Visit API docs: http://localhost:3001/docs
