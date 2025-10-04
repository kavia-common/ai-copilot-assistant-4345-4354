import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import httpx

from ..pydantic_models import AskRequest, AskResponse
from .openai_client import get_answer

logger = logging.getLogger(__name__)
router = APIRouter()

# PUBLIC_INTERFACE
@router.post(
    "/api/ask",
    response_model=AskResponse,
    tags=["qa"],
    summary="Ask a question",
    description="Send a question to the AI model and get a generated answer.",
)
async def ask(req: AskRequest):
    """
    Handle the /api/ask endpoint.

    - Validates the question and returns 400 if empty.
    - Calls the OpenAI client to generate an answer.
    - Maps errors to appropriate HTTP codes:
        * 400: empty question or missing OPENAI_API_KEY
        * 502: upstream provider/network errors
        * 500: unexpected exceptions
    """
    try:
        q = (req.question or "").strip()
        logger.info("Received /api/ask. Prompt length=%d snippet=%r", len(q), q[:120])

        if not q:
            logger.warning("Empty question received for /api/ask")
            raise HTTPException(status_code=400, detail="Question must not be empty.")

        # Call OpenAI via our client helper
        answer_text, model_used = await get_answer(q)
        return AskResponse(answer=answer_text, model=model_used)

    except HTTPException as he:
        # Known client-side issues
        logger.warning("HTTPException in /api/ask: %s (%s)", he.detail, type(he).__name__)
        return JSONResponse(
            status_code=he.status_code,
            content={"message": "Bad request", "detail": he.detail},
        )
    except ValueError as ve:
        # Typically configuration errors like missing OPENAI_API_KEY
        detail_str = str(ve)
        logger.warning("Configuration error in /api/ask: %s", detail_str)
        return JSONResponse(
            status_code=400,
            content={
                "message": "Configuration error",
                "detail": detail_str,
                "action": "Set OPENAI_API_KEY in backend environment and retry.",
            },
        )
    except httpx.HTTPStatusError as hse:
        # Upstream responded with non-2xx
        logger.error("Upstream HTTPStatusError in /api/ask: %s", str(hse), exc_info=True)
        return JSONResponse(
            status_code=502,
            content={
                "message": "Upstream AI provider error",
                "detail": str(hse),
                "hint": "Verify your model name, API key, and account quota.",
            },
        )
    except httpx.HTTPError as he:
        # Network or request issues
        logger.error("Upstream HTTPError in /api/ask: %s", str(he), exc_info=True)
        return JSONResponse(
            status_code=502,
            content={
                "message": "Network error contacting AI provider",
                "detail": str(he),
                "hint": "Check network connectivity and provider base URL.",
            },
        )
    except Exception as ex:
        # Unexpected errors
        logger.exception("Unhandled exception in /api/ask: %s (%s)", str(ex), type(ex).__name__)
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error", "detail": "An unexpected error occurred."},
        )
