import requests

from app.config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL


def groq_chat_completion(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0,
    max_tokens: int = 1024,
    timeout: int = 120,
    api_key: str | None = None,
    model: str | None = None,
) -> str:
    resolved_api_key = api_key or GROQ_API_KEY
    resolved_model = model or GROQ_MODEL
    if not resolved_api_key:
        raise RuntimeError("GROQ_API_KEY is required for RAG SQL generation")

    response = requests.post(
        f"{GROQ_BASE_URL.rstrip('/')}/chat/completions",
        headers={
            "Authorization": f"Bearer {resolved_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": resolved_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()
