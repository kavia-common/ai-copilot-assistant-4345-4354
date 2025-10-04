from fastapi import APIRouter, HTTPException
import httpx
from ..pydantic_models import AskRequest, AskResponse
from . import openai_client

router = APIRouter(prefix="/api", tags=["qa"])

# PUBLIC_INTERFACE
@router.get("/health", summary="Health check", description="Simple health endpoint to verify the API is running.")
async def health():
    """Return service health status."""
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
async def ask(request: AskRequest) -> AskResponse:
    """Accept a question and return an AI-generated answer."""
    try:
        answer, model = await openai_client.get_answer(request.question)
        return AskResponse(answer=answer, model=model)
    except ValueError as e:
        # Typically missing OPENAI_API_KEY
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
