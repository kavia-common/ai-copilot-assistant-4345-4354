import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .deps import settings

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

    # CORS configuration - defaults plus FRONTEND_ORIGIN if provided
    origins = {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    }
    if settings.FRONTEND_ORIGIN:
        origins.add(settings.FRONTEND_ORIGIN)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request logging middleware for diagnostics
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all incoming requests and responses for diagnostics."""
        start_time = time.time()
        logger = logging.getLogger("uvicorn.access")
        
        # Log incoming request
        logger.info(
            "Incoming request: %s %s from %s (Origin: %s)",
            request.method,
            request.url.path,
            request.client.host if request.client else "unknown",
            request.headers.get("origin", "none"),
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(
                "Request completed: %s %s -> %s (%.3fs)",
                request.method,
                request.url.path,
                response.status_code,
                process_time,
            )
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "Request failed: %s %s (%.3fs) - %s",
                request.method,
                request.url.path,
                process_time,
                str(e),
                exc_info=True,
            )
            # Return JSON error response for unhandled exceptions
            return JSONResponse(
                status_code=500,
                content={
                    "message": "Internal server error",
                    "detail": "An unexpected error occurred while processing the request.",
                },
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
