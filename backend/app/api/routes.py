from fastapi import APIRouter
from pydantic import BaseModel

from app.services.github_loader import GitHubLoader
from app.orchestrator.hermes_orchestrator import (
    HermesOrchestrator,
)

router = APIRouter()

github_loader = GitHubLoader()
orchestrator = HermesOrchestrator()


class RepoRequest(BaseModel):
    repo_url: str


@router.get("/")
async def root():
    return {
        "message": "Hermes Engineering Crew API Running"
    }


@router.post("/analyze-repo")
async def analyze_repo(request: RepoRequest):

    repository_files = (
        await github_loader.fetch_repository_contents(
            request.repo_url
        )
    )

    report = await orchestrator.run_analysis(
        repository_files
    )

    return report