import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()

class AskRequest(BaseModel):
    question: str = Field(..., description="The user's question to be answered by the AI.")

class AskResponse(BaseModel):
    answer: str = Field(..., description="The AI-generated answer for the given question.")
    model: Optional[str] = Field(None, description="The model used to generate the answer, if available.")

# PUBLIC_INTERFACE
@router.post(
    "/api/ask",
    response_model=AskResponse,
    tags=["qa"],
    summary="Ask a question",
    description="Send a question to the AI model and get a generated answer.",
)
def ask(req: AskRequest):
    """
    Handle the /api/ask endpoint.
    - Logs incoming request prompt length/snippet.
    - Returns a static answer as placeholder (adjust to real OpenAI integration elsewhere).
    - Logs and returns structured errors when exceptions occur.
    """
    try:
        q = (req.question or "").strip()
        # Log incoming prompt length and a safe snippet (first 120 chars)
        logger.info("Received /api/ask. Prompt length=%d snippet=%r", len(q), q[:120])

        if not q:
            # Log and raise a 400
            logger.warning("Empty question received for /api/ask")
            raise HTTPException(status_code=400, detail="Question must not be empty.")

        # Placeholder logic; in real app this would call OpenAI and may raise
        answer_text = f"You asked: {q}\n\nThis is a placeholder response from the backend."

        return AskResponse(answer=answer_text, model=None)

    except HTTPException as he:
        # Log known http exceptions
        logger.exception("HTTPException in /api/ask: %s (%s)", he.detail, type(he).__name__)
        return JSONResponse(status_code=he.status_code, content={"message": "Bad request", "detail": he.detail})
    except Exception as ex:
        # Log unexpected exceptions with stack trace
        logger.exception("Unhandled exception in /api/ask: %s (%s)", str(ex), type(ex).__name__)
        return JSONResponse(status_code=500, content={"message": "Internal server error", "detail": str(ex)})
