import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# PUBLIC_INTERFACE
def create_app():
    """Create and configure the FastAPI application with basic logging and CORS."""
    # Configure basic logging if not already configured
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("uvicorn.error")
    logger.info("Starting AI Copilot Backend with basic logging enabled")

    app = FastAPI(
        title="AI Copilot Backend",
        description="Backend API for an AI Copilot that answers user questions using Google Gemini.",
        version="0.1.0",
        openapi_tags=[
            {"name": "qa", "description": "Ask questions and get AI-generated answers."},
            {"name": "system", "description": "System endpoints like health checks."},
        ],
    )

    # CORS configuration - match README guidance
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    # Allow override via FRONTEND_ORIGIN env if middleware defined elsewhere; kept minimal here.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routers if they exist
    try:
        from .routers import ask  # type: ignore
        app.include_router(ask.router)
    except Exception as e:
        logging.getLogger(__name__).warning("Routers not found or failed to include: %s", e)

    @app.get("/", tags=["system"], summary="Health Check", description="Basic health check of the service.")
    def health_check():
        """Health check to verify service is running."""
        return {"status": "ok"}

    @app.get("/api/health", tags=["qa"], summary="Health check", description="Simple health endpoint to verify the API is running.")
    def api_health():
        """Health endpoint."""
        return {"ok": True}

    return app


# Create the app for ASGI servers
app = create_app()
