import httpx
from ..deps import settings

api_key = settings.OPENAI_API_KEY
base_url = settings.OPENAI_BASE_URL.rstrip("/")
model = settings.OPENAI_MODEL

# PUBLIC_INTERFACE
async def get_answer(question: str) -> tuple[str, str]:
    """Call OpenAI Chat Completions API to get an answer for the given question.
    
    Returns a tuple of (answer, model_used).
    Raises httpx.HTTPError for HTTP issues; other exceptions for unexpected errors.
    """
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY. Please configure the service.")

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
        resp.raise_for_status()
        data = resp.json()
        answer = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        ) or ""
        used_model = data.get("model", model)
        return answer, used_model
