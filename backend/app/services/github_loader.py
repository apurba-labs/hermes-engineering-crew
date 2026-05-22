import httpx
from typing import Dict, List

# Broadened extension tracking parameters matching your setup profile
SUPPORTED_EXTENSIONS = (
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".php",
    ".go",
    ".java",
    ".rs",
    ".md",
)

class GitHubLoader:
    def __init__(self):
        self.timeout = 20.0
        self.max_files = 30

    async def fetch_repository_contents(self, repo_url: str) -> Dict[str, str]:
        """
        Extracts repository signatures and instantiates a recursive
        asynchronous walk across nested system scopes.
        """
        repo_path = self.extract_repo_path(repo_url)
        files_payload = {}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            await self.walk_contents(
                client=client,
                repo_path=repo_path,
                path="",
                files_payload=files_payload,
            )

        return files_payload

    def extract_repo_path(self, repo_url: str) -> str:
        """
        Sanitizes trailing strings and extracts ownership keys.
        """
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
        # Defensive termination if boundary cap parameters are matched
        if len(files_payload) >= self.max_files:
            return

        # Ensure safe character encoding over deep directory structures
        api_url = f"https://api.github.com/repos/{repo_path}/contents/{path}"
        
        try:
            response = await client.get(api_url)
            if response.status_code != 200:
                return
                
            contents = response.json()
            
            # If the response isn't a directory array list block, safely drop back
            if not isinstance(contents, list):
                return

            for item in contents:
                if len(files_payload) >= self.max_files:
                    break

                item_type = item.get("type")

                # Handle Nested Subdirectory Blocks
                if item_type == "dir":
                    await self.walk_contents(
                        client=client,
                        repo_path=repo_path,
                        path=item["path"],
                        files_payload=files_payload,
                    )

                # Process Target Core File Buffers
                elif item_type == "file":
                    file_name = item.get("name", "")
                    
                    if not file_name.endswith(SUPPORTED_EXTENSIONS):
                        continue

                    download_url = item.get("download_url")
                    if not download_url:
                        continue

                    file_response = await client.get(download_url)
                    if file_response.status_code == 200:
                        # Slice content strictly to safely guard context horizons
                        files_payload[item["path"]] = file_response.text[:15000]

        except Exception as e:
            # Prevent single file tracking failures from stalling the entire agent crew workflow
            print(f"[GitHubLoader Warning] Bypassing structural node layout exception: {str(e)}")
            return