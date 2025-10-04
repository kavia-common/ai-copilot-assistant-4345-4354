import httpx
from ..deps import settings

api_key = settings.OPENAI_API_KEY
base_url = settings.OPENAI_BASE_URL.rstrip("/")
model = settings.OPENAI_MODEL

# PUBLIC_INTERFACE
async def get_answer(question: str) -> tuple[str, str]:
    """Call OpenAI Chat Completions API to get an answer for the given question.
    
    Returns:
        (answer, model_used)
    Raises:
        ValueError: When configuration like OPENAI_API_KEY is missing.
        httpx.HTTPError: For HTTP/network issues.
    """
    if not api_key:
        # Provide a clear, actionable message
        raise ValueError(
            "Missing OPENAI_API_KEY. Please set OPENAI_API_KEY in the backend environment. "
            "The service can run without it, but /api/ask requires a valid key."
        )

    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful, concise AI assistant."},
            {"role": "user", "content": question},
        ],
        "temperature": 0.2,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        # If not OK, raise for status so caller can handle httpx.HTTPStatusError
        resp.raise_for_status()
        data = resp.json()
        answer = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        ) or ""
        used_model = data.get("model", model)
        return answer, used_model
