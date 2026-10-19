import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.logging import logger

class GitHubClient:
    """
    Interacts with the GitHub API to query repository metadata, tree structure,
    branches, commits, and rate limits.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, owner: Optional[str] = None, repo: Optional[str] = None, token: Optional[str] = None):
        self.owner = owner or settings.GITHUB_OWNER
        self.repo = repo or settings.GITHUB_REPO
        self.token = token or settings.GITHUB_TOKEN

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Autoryx-Assignment-Agent/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def get_repo_status(self) -> Dict[str, Any]:
        """Checks connection status and access to the target repository."""
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(url, headers=self._get_headers())
                remaining = res.headers.get("x-ratelimit-remaining")
                rate_limit = int(remaining) if remaining else None

                if res.status_code == 200:
                    data = res.json()
                    return {
                        "is_connected": True,
                        "owner": self.owner,
                        "repo": self.repo,
                        "default_branch": data.get("default_branch", "main"),
                        "target_isolated_dir": settings.TARGET_ISOLATED_DIR,
                        "message": f"Successfully connected to {self.owner}/{self.repo} (default branch: {data.get('default_branch', 'main')})",
                        "rate_limit_remaining": rate_limit
                    }
                elif res.status_code == 404:
                    return {
                        "is_connected": False,
                        "owner": self.owner,
                        "repo": self.repo,
                        "default_branch": settings.GITHUB_DEFAULT_BRANCH,
                        "target_isolated_dir": settings.TARGET_ISOLATED_DIR,
                        "message": f"Repository '{self.owner}/{self.repo}' not found or token has insufficient permissions.",
                        "rate_limit_remaining": rate_limit
                    }
                elif res.status_code == 401:
                    return {
                        "is_connected": False,
                        "owner": self.owner,
                        "repo": self.repo,
                        "default_branch": settings.GITHUB_DEFAULT_BRANCH,
                        "target_isolated_dir": settings.TARGET_ISOLATED_DIR,
                        "message": "Invalid or expired GitHub token.",
                        "rate_limit_remaining": rate_limit
                    }
                else:
                    return {
                        "is_connected": False,
                        "owner": self.owner,
                        "repo": self.repo,
                        "default_branch": settings.GITHUB_DEFAULT_BRANCH,
                        "target_isolated_dir": settings.TARGET_ISOLATED_DIR,
                        "message": f"GitHub API responded with code {res.status_code}: {res.text[:150]}",
                        "rate_limit_remaining": rate_limit
                    }
            except Exception as e:
                logger.error(f"Error checking GitHub status: {e}")
                return {
                    "is_connected": False,
                    "owner": self.owner,
                    "repo": self.repo,
                    "default_branch": settings.GITHUB_DEFAULT_BRANCH,
                    "target_isolated_dir": settings.TARGET_ISOLATED_DIR,
                    "message": f"Network error connecting to GitHub: {str(e)}",
                    "rate_limit_remaining": None
                }

    async def get_contents(self, path: str = "", ref: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists directory contents or fetches file info at the given path."""
        url = f"{self.BASE_URL}/repos/{self.owner}/{self.repo}/contents/{path.strip('/')}"
        params = {}
        if ref:
            params["ref"] = ref

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(url, headers=self._get_headers(), params=params)
                if res.status_code == 200:
                    data = res.json()
                    if isinstance(data, list):
                        return data
                    return [data]
                return []
            except Exception as e:
                logger.error(f"Error fetching contents for {path}: {e}")
                return []

    async def get_raw_file(self, path: str, ref: str = "main") -> Optional[str]:
        """Fetches raw text content of a file."""
        url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{ref}/{path.strip('/')}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(url, headers=self._get_headers())
                if res.status_code == 200:
                    return res.text
                return None
            except Exception as e:
                logger.error(f"Error fetching raw file {path}: {e}")
                return None
