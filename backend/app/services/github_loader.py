import httpx
import time
import logging
from typing import Dict
from app.core.config import settings
from fastapi import HTTPException

logger = logging.getLogger("hermes.services.github")

class GitHubLoader:
    def __init__(self):
        # Read from renamed explicit fallback configs
        self.timeout = float(settings.GITHUB_FETCH_TIMEOUT)
        self.max_files = settings.MAX_REPO_FILES
        self.supported_extensions = settings.SUPPORTED_EXTENSIONS
        self.github_token = settings.GITHUB_TOKEN

    async def fetch_repository_contents(self, repo_url: str, github_token: str = None) -> Dict[str, str]:
        start_time = time.perf_counter()
        repo_path = self.extract_repo_path(repo_url)
        files_payload = {}

        headers = {
            "User-Agent": "Gotihub-Hermes-Orchestrator-Engine/1.0",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Priority token mapping check
        active_token = github_token if github_token and github_token.strip() else self.github_token
        if active_token and active_token.strip():
            headers["Authorization"] = f"token {active_token.strip()}"
            logger.info("[GitHubLoader] Authentication headers loaded into client workspace.")

        async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as client:
            # We initiate the recursive traversal loop
            await self.walk_contents(
                client=client,
                repo_path=repo_path,
                path="",
                files_payload=files_payload,
            )
            
        # Raise an exception if the entire run yielded absolutely no files
        if not files_payload:
            logger.error(f"[GitHubLoader Error] Extraction failed. No files recovered for {repo_path}")
            raise HTTPException(
                status_code=400, 
                detail="The requested repository content tree is empty, inaccessible, or contains no matching extensions."
            )

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
        
        contents = None
        # THE REFIX MATRIX: Attempt branches sequentially without crashing on 404
        for branch in ["main", "master"]:
            api_url = f"https://api.github.com/repos/{repo_path}/contents/{path}?ref={branch}"
            try:
                response = await client.get(api_url)
                if response.status_code == 200:
                    contents = response.json()
                    if isinstance(contents, list):
                        break  # Found the active branch layout! Break out of branch loop.
                else:
                    logger.debug(f"[GitHubLoader Branch Check] Branch '{branch}' returned status code: {response.status_code}")
            except httpx.HTTPStatusError as http_err:
                logger.debug(f"[GitHubLoader Branch Check] Branch '{branch}' failed with HTTP error: {http_err}")
            except Exception as e:
                logger.debug(f"[GitHubLoader Network Warning] Branch check failed for '{branch}': {str(e)}")
                continue

        # If after checking both branches nothing is found, return safely from this branch line
        if contents is None or not isinstance(contents, list):
            logger.warning(f"[GitHubLoader Warning] Inaccessible directory mapping state for node: '{path}'")
            return

        # Process the directory items recovered from the successful branch validation loop
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
                
                # Check file extension types matching criteria bounds
                if not file_name.endswith(self.supported_extensions):
                    continue

                download_url = item.get("download_url")
                if not download_url:
                    continue

                try:
                    file_response = await client.get(download_url)
                    if file_response.status_code == 200:
                        # Slice content length window matching system limits safely
                        files_payload[item["path"]] = file_response.text[:15000]
                except Exception as file_err:
                    logger.warning(f"[GitHubLoader Warning] Failed streaming file node context: {str(file_err)}")
                    continue