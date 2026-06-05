from app.config import settings

_client = None


def generate(system: str, user_message: str) -> str:
    """Send a single-shot, source-grounded request to the LLM and return the text."""
    client = _get_client()
    response = client.chat.completions.create(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content or ""


def _get_client():
    global _client
    if _client is None:
        # Lazy import — keeps module import cheap and avoids requiring a key in tests.
        import openai
        _client = openai.OpenAI(api_key=settings.openai_api_key)
    return _client
