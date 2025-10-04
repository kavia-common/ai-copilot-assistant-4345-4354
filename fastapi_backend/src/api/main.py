from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .deps import settings
from .routers import ask

openapi_tags = [
    {"name": "qa", "description": "Ask questions and get AI-generated answers."},
    {"name": "system", "description": "System endpoints like health checks."},
]

app = FastAPI(
    title="AI Copilot Backend",
    description="Backend API for an AI Copilot that answers user questions using OpenAI.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# Build allowed origins list, always include explicit localhost variants for local dev.
# Explicitly avoid allow_credentials when using wildcard-ish patterns.
allowed_origins = {
    settings.FRONTEND_ORIGIN,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}
# Note: You can extend with additional preview hosts via FRONTEND_ORIGIN or by editing this list.

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_origins),
    allow_credentials=False,  # WithCredentials disabled to avoid preflight+cookie constraints for local dev
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(ask.router)

# Root path for basic health - documented under system
@app.get(
    "/",
    tags=["system"],
    summary="Health Check",
    description="Basic health check of the service."
)
def health_check():
    """Return a simple health status payload."""
    return {"message": "Healthy"}
