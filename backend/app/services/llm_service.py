import httpx
import logging
from typing import Dict, Any, Union
from app.core.config import settings

logger = logging.getLogger("hermes.services.llm")

class LLMService:

    def __init__(self):
        # Fallback configs from core system settings
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.default_model = settings.WORKER_MODEL
        self.timeout = getattr(settings, "WORKER_TIMEOUT", 120.0)

    async def generate_response(self, payload: Union[str, Dict[str, Any]]) -> str:
        """
        Processes incoming agent requests. If given a dictionary, it routes straight 
        to /api/chat. If given a string, it routes cleanly to /api/generate.
        """
        async with httpx.AsyncClient() as client:
            try:
                # Scenario A: Agent sends a fully structured, production multi-turn dictionary payload
                if isinstance(payload, dict):
                    # Ensure a fallback model is designated if not explicitly defined inside the payload
                    if "model" not in payload or not payload["model"]:
                        payload["model"] = self.default_model
                        
                    target_url = f"{self.base_url}/api/chat"
                    logger.info(f"[LLMService] Routing structured dictionary matrix to endpoint: {target_url}")
                    
                    response = await client.post(
                        target_url,
                        json=payload,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extract string cleanly from Ollama's Chat API schema model
                    return data["message"]["content"]

                # Scenario B: Legacy/Fallback single raw text prompt string handling
                else:
                    target_url = f"{self.base_url}/api/generate"
                    logger.info(f"[LLMService] Routing flat prompt string string to endpoint: {target_url}")
                    
                    flat_payload = {
                        "model": self.default_model,
                        "prompt": str(payload),
                        "stream": False,
                    }
                    
                    response = await client.post(
                        target_url,
                        json=flat_payload,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extract string cleanly from Ollama's Completion API schema model
                    return data.get("response", "")

            except httpx.HTTPStatusError as http_err:
                logger.error(f"[LLMService HTTP Error] Status {http_err.response.status_code}: {http_err.response.text}")
                raise Exception(f"Ollama execution node rejected payload: {http_err.response.text}")
            except Exception as e:
                logger.error(f"[LLMService Exception] Critical communication breakdown: {str(e)}")
                raise e