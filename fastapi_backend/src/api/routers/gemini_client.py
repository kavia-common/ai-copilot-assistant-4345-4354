import logging
import asyncio
from typing import Tuple

import google.generativeai as genai

from ..deps import settings

logger = logging.getLogger(__name__)

# Configure Google Generative AI with API key from environment on import.
# We avoid doing expensive work at import time; model is created lazily.
if settings.GOOGLE_GEMINI_API_KEY:
    genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)


class GeminiConfigurationError(ValueError):
    """Raised when Gemini configuration is invalid (e.g., missing API key)."""


class GeminiUpstreamError(RuntimeError):
    """Raised when an upstream error occurs while calling Gemini."""


def _get_model():
    """Create and return the GenerativeModel instance for current settings."""
    try:
        return genai.GenerativeModel(settings.GEMINI_MODEL)
    except Exception as e:  # pragma: no cover - defensive
        logger.exception("Failed to create GenerativeModel: %s", e)
        raise GeminiUpstreamError(f"Failed to initialize Gemini model: {e}") from e


# PUBLIC_INTERFACE
async def get_answer(question: str, timeout: float = 30.0) -> Tuple[str, str]:
    """Get an answer from Google Gemini for the provided question.

    Args:
        question: The user's question to be answered.
        timeout: Maximum time in seconds to wait for a response (default: 30s).

    Returns:
        tuple(answer, model_used)

    Raises:
        GeminiConfigurationError: Missing API key or invalid configuration.
        GeminiUpstreamError: Upstream provider/network errors or timeout.
        Exception: Any other unexpected exceptions.
    """
    if not settings.GOOGLE_GEMINI_API_KEY:
        raise GeminiConfigurationError(
            "Missing GOOGLE_GEMINI_API_KEY. Please set GOOGLE_GEMINI_API_KEY in the backend environment. "
            "The service can run without it, but /api/ask requires a valid key."
        )

    try:
        model = _get_model()
        # Wrap the synchronous SDK call in an executor with timeout
        loop = asyncio.get_event_loop()
        
        async def _generate_with_timeout():
            try:
                # Run the blocking call in a thread pool
                resp = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content([{"role": "user", "parts": [question]}])
                )
                return resp
            except asyncio.CancelledError:
                raise GeminiUpstreamError("Request timeout: The AI provider took too long to respond.")
        
        # Apply timeout
        resp = await asyncio.wait_for(_generate_with_timeout(), timeout=timeout)
        
        # The SDK generally returns text on resp.text; fallback to empty string if not present.
        answer_text = (getattr(resp, "text", None) or "").strip()
        return answer_text, settings.GEMINI_MODEL
    except asyncio.TimeoutError as te:
        logger.error("Gemini request timeout after %s seconds", timeout)
        raise GeminiUpstreamError(f"Request timeout: AI provider took longer than {timeout}s to respond.") from te
    except GeminiUpstreamError:
        # Re-raise our own errors
        raise
    except Exception as e:
        # Map all SDK-specific problems to a single upstream error for downstream HTTP mapping.
        logger.error("Gemini upstream error: %s", e, exc_info=True)
        raise GeminiUpstreamError(str(e)) from e
