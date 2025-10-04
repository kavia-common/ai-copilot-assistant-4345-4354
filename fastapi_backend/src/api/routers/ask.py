from fastapi import APIRouter
from fastapi.responses import JSONResponse
import httpx
from ..pydantic_models import AskRequest, AskResponse
from . import openai_client

router = APIRouter(prefix="/api", tags=["qa"])

# PUBLIC_INTERFACE
@router.get(
    "/health",
    summary="Health check",
    description="Simple health endpoint to verify the API is running.",
    responses={200: {"description": "Service healthy"}})
async def health():
    """Return service health status as JSON with HTTP 200."""
    return {"status": "ok"}

# PUBLIC_INTERFACE
@router.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask a question",
    description="Send a question to the AI model and get a generated answer.",
    responses={
        200: {"description": "Answer successfully generated."},
        400: {"description": "Bad request or missing configuration."},
        502: {"description": "Upstream AI provider error."},
        500: {"description": "Internal server error."},
    },
)
async def ask(request: AskRequest):
    """
    Accept a question and return an AI-generated answer.

    Returns:
        AskResponse JSON on success. JSON error with 'message' on failures.
    """
    try:
        answer, model = await openai_client.get_answer(request.question)
        return AskResponse(answer=answer, model=model)
    except ValueError as e:
        # Typically missing OPENAI_API_KEY or invalid configuration
        return JSONResponse(
            status_code=400,
            content={"message": str(e)},
        )
    except httpx.HTTPStatusError as e:
        # Upstream returned a non-2xx code; surface a helpful message
        detail = e.response.text if e.response is not None else str(e)
        return JSONResponse(
            status_code=502,
            content={"message": "Upstream AI provider error", "detail": detail},
        )
    except httpx.HTTPError as e:
        # Network or protocol level errors
        return JSONResponse(
            status_code=502,
            content={"message": "Network error when contacting AI provider", "detail": str(e)},
        )
    except Exception as e:
        # Unexpected server error
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "detail": str(e)},
        )
