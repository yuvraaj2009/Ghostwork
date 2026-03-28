from google import genai
from app.config import get_settings

_client = None


def get_ai_client() -> genai.Client:
    global _client
    if _client is None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


async def generate(prompt: str, system_instruction: str | None = None) -> str:
    """Generate text using Gemini. Single function, easy to swap later."""
    client = get_ai_client()
    model = get_settings().gemini_model

    config = {}
    if system_instruction:
        config["system_instruction"] = system_instruction

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config if config else None,
    )
    return response.text
