import httpx
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from app.core.config import settings
from app.services.github_loader import GitHubLoader
from app.orchestrator.hermes_orchestrator import HermesOrchestrator

logger = logging.getLogger("hermes.api")
router = APIRouter()

# Instantiate core platform components
github_loader = GitHubLoader()
orchestrator = HermesOrchestrator()


class RepoRequest(BaseModel):
    repo_url: str


@router.get("/")
async def root():
    return {
        "status": "healthy",
        "message": "Hermes Engineering Crew API Running"
    }


@router.get("/api/ai-check")
async def verify_local_llm():
    """Verifies if the backend API layer can cleanly communicate with the Ollama service."""
    # Build the endpoint cleanly from core configurations
    ollama_tags_url = f"{settings.OLLAMA_URL}/api/tags"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(ollama_tags_url, timeout=5.0)
            if response.status_code == 200:
                return {"ollama_connection": "successful", "models": response.json()}
            return {
                "ollama_connection": "failed", 
                "error": f"Ollama service returned status code {response.status_code}"
            }
    except Exception as e:
        logger.error(f"[Gateway Check Failure]: Ollama node unreachable. Error: {str(e)}")
        return {"ollama_connection": "failed", "error": str(e)}


@router.post("/analyze-repo")
async def analyze_repo(request: RepoRequest):
    """
    Triggers the high-performance multi-agent scanning sequence over the target repository.
    """
    logger.info(f"[API Route] Initializing analysis request for target: {request.repo_url}")
    
    try:
        # 1. Pull down repository files into temporary buffer memory
        repository_files = await github_loader.fetch_repository_contents(
            request.repo_url
        )
        
        if not repository_files:
            raise HTTPException(
                status_code=400, 
                detail="The requested repository content tree is empty or inaccessible."
            )

        # 2. ⚡ FIXED: Correctly pass BOTH arguments matching your production orchestration signature
        report = await orchestrator.run_analysis(
            repo_url=request.repo_url,
            repository_files=repository_files
        )

        return report

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.error(f"[API Route Exception]: Critical failure in analysis route pipeline. Trace: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Hermes Orchestration pipeline failed to compute target mapping: {str(e)}"
        )