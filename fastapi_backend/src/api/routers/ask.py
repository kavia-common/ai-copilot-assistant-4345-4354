import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..pydantic_models import AskRequest, AskResponse
from .gemini_client import get_answer, GeminiConfigurationError, GeminiUpstreamError

logger = logging.getLogger(__name__)
router = APIRouter()

# PUBLIC_INTERFACE
@router.post(
    "/api/ask",
    response_model=AskResponse,
    tags=["qa"],
    summary="Ask a question",
    description="Send a question to the AI model (Google Gemini) and get a generated answer.",
)
async def ask(req: AskRequest):
    """
    Handle the /api/ask endpoint.

    - Validates the question and returns 400 if empty.
    - Calls the Gemini client to generate an answer.
    - Maps errors to appropriate HTTP codes:
        * 400: empty question or missing GOOGLE_GEMINI_API_KEY
        * 502: upstream provider/network errors
        * 500: unexpected exceptions
    """
    try:
        q = (req.question or "").strip()
        logger.info("Received /api/ask. Prompt length=%d snippet=%r", len(q), q[:120])

        if not q:
            logger.warning("Empty question received for /api/ask")
            raise HTTPException(status_code=400, detail="Question must not be empty.")

        # Call Gemini via our client helper
        answer_text, model_used = await get_answer(q)
        return AskResponse(answer=answer_text, model=model_used)

    except HTTPException as he:
        # Known client-side issues
        logger.warning("HTTPException in /api/ask: %s (%s)", he.detail, type(he).__name__)
        return JSONResponse(
            status_code=he.status_code,
            content={"message": "Bad request", "detail": he.detail},
        )
    except GeminiConfigurationError as ve:
        # Typically configuration errors like missing GOOGLE_GEMINI_API_KEY
        detail_str = str(ve)
        logger.warning("Configuration error in /api/ask: %s", detail_str)
        return JSONResponse(
            status_code=400,
            content={
                "message": "Configuration error",
                "detail": detail_str,
                "action": "Set GOOGLE_GEMINI_API_KEY in backend environment and retry.",
            },
        )
    except GeminiUpstreamError as ge:
        logger.error("Upstream provider error in /api/ask: %s", str(ge), exc_info=True)
        return JSONResponse(
            status_code=502,
            content={
                "message": "Upstream AI provider error",
                "detail": str(ge),
                "hint": "Verify your model name, API key, and account quota.",
            },
        )
    except Exception as ex:
        # Unexpected errors
        logger.exception("Unhandled exception in /api/ask: %s (%s)", str(ex), type(ex).__name__)
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "detail": "An unexpected error occurred."},
        )
