import httpx
import os
import time
import logging
from typing import Dict, List
from app.core.config import settings

logger = logging.getLogger("hermes.services.github")

class GitHubLoader:
    def __init__(self):
        self.timeout = 20.0
        self.max_files = settings.MAX_REPO_FILES
        self.supported_extensions = settings.SUPPORTED_EXTENSIONS
        
        # Bring in your corporate github token from system variables if available
        self.github_token = settings.GITHUB_TOKEN

    async def fetch_repository_contents(self, repo_url: str) -> Dict[str, str]:
        # Start timer for GitHub downloads
        start_time = time.perf_counter()
        
        repo_path = self.extract_repo_path(repo_url)
        files_payload = {}

        # Inject the mandatory headers directly into the base client layout
        headers = {
            "User-Agent": "Gotihub-Hermes-Orchestrator-Engine/1.0",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Authenticate if a token exists to unlock 5,000 requests per hour
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
            logger.info("[GitHubLoader] Outbound authorization token loaded successfully.")

        async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as client:
            await self.walk_contents(
                client=client,
                repo_path=repo_path,
                path="",
                files_payload=files_payload,
            )
            
        # Stop timer and calculate total download duration
        elapsed = time.perf_counter() - start_time
        print(f"\n[TELEMETRY] GitHubLoader fetched {len(files_payload)} files in {elapsed:.2f} seconds.")
        
        return files_payload

    def extract_repo_path(self, repo_url: str) -> str:
        parts = repo_url.rstrip("/").split("github.com/")
        if len(parts) < 2:
            raise ValueError("Invalid GitHub repository URL configuration.")
        return parts[1]

    async def walk_contents(
        self,
        client: httpx.AsyncClient,
        repo_path: str,
        path: str,
        files_payload: Dict[str, str],
    ):
        if len(files_payload) >= self.max_files:
            return

        api_url = f"https://api.github.com/repos/{repo_path}/contents/{path}"
        
        try:
            response = await client.get(api_url)
            
            # Better visibility: Log problems instead of dropping out silently
            if response.status_code != 200:
                logger.error(f"[GitHubLoader Error] Target node returned status: {response.status_code} for path: '{path}'")
                return
                
            contents = response.json()
            if not isinstance(contents, list):
                return

            for item in contents:
                if len(files_payload) >= self.max_files:
                    break

                item_type = item.get("type")

                if item_type == "dir":
                    await self.walk_contents(
                        client=client,
                        repo_path=repo_path,
                        path=item["path"],
                        files_payload=files_payload,
                    )

                elif item_type == "file":
                    file_name = item.get("name", "")
                    
                    # Target extensions verify pass
                    if not file_name.endswith(self.supported_extensions):
                        continue

                    download_url = item.get("download_url")
                    if not download_url:
                        continue

                    file_response = await client.get(download_url)
                    if file_response.status_code == 200:
                        files_payload[item["path"]] = file_response.text[:15000]

        except Exception as e:
            logger.warning(f"[GitHubLoader Warning] Bypassing structural node layout exception: {str(e)}")
            return