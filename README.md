# AI Copilot - Backend Workspace

This workspace contains the FastAPI backend for the AI Copilot application. The paired React frontend lives in a separate workspace (`ai-copilot-assistant-4345-4355`).

## What was added
- FastAPI app with CORS and OpenAPI docs
- Endpoints:
  - GET / and GET /api/health
  - POST /api/ask with body { question: string }
- OpenAI integration via environment variables

## Running
- Copy `fastapi_backend/.env.example` to `fastapi_backend/.env` and set variables (OPENAI_API_KEY for real responses).
- Install dependencies: `pip install -r fastapi_backend/requirements.txt`
- Start server: `uvicorn fastapi_backend.src.api.main:app --host 0.0.0.0 --port 3001`
- Open http://localhost:3001/docs

The frontend will call http://localhost:3001/api/ask.
