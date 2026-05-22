import httpx
from app.core.config import settings

class LLMService:

    def __init__(self):

        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def generate_response(
        self,
        prompt: str
    ) -> str:

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        async with httpx.AsyncClient() as client:

            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=settings.OLLAMA_TIMEOUT,
            )

            response.raise_for_status()

            data = response.json()

            return data.get("response", "")