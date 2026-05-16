"""
GitHub API client for fetching PR information and diffs.
"""
import httpx
from typing import Dict, Any, Optional
from backend.config import settings


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self):
        self.base_url = settings.github_api_url
        self.token = settings.github_token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def get_pr_info(self, owner: str, repo: str, pr_number: str) -> Dict[str, Any]:
        """
        Fetch PR information from GitHub.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            Dictionary with PR information
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    
    async def get_pr_diff(self, owner: str, repo: str, pr_number: str) -> str:
        """
        Fetch PR diff in unified format.
        
        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            
        Returns:
            Unified diff string
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        # Request diff format
        headers = {
            **self.headers,
            "Accept": "application/vnd.github.v3.diff"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.text
    
    async def get_file_content(
        self, 
        owner: str, 
        repo: str, 
        file_path: str, 
        ref: Optional[str] = None
    ) -> str:
        """
        Fetch file content from repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            file_path: Path to file in repository
            ref: Git reference (branch, tag, commit SHA). Defaults to default branch.
            
        Returns:
            File content as string
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
        params = {"ref": ref} if ref else {}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, 
                headers=self.headers, 
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Decode base64 content
            import base64
            content = base64.b64decode(data["content"]).decode("utf-8")
            return content
    
    def parse_repository(self, repository: str) -> tuple[str, str]:
        """
        Parse repository string into owner and repo name.
        
        Args:
            repository: Repository in format "owner/repo"
            
        Returns:
            Tuple of (owner, repo)
        """
        parts = repository.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid repository format: {repository}. Expected 'owner/repo'")
        return parts[0], parts[1]

# Made with Bob
