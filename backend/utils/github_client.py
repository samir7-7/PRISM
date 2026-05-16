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
        
        # Only include Authorization header if token is provided
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
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
        
        # Retry with exponential backoff
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=self.headers, timeout=30.0)
                    
                    # Handle rate limiting
                    if response.status_code == 403:
                        # Check if it's rate limit
                        if 'X-RateLimit-Remaining' in response.headers:
                            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                            if remaining == 0:
                                # Rate limited - check reset time
                                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                                import time
                                wait_time = max(reset_time - time.time(), retry_delay)
                                
                                if attempt < max_retries - 1:
                                    import asyncio
                                    await asyncio.sleep(min(wait_time, 60))  # Cap at 60 seconds
                                    continue
                    
                    response.raise_for_status()
                    return response.json()
                    
            except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
                if attempt == max_retries - 1:
                    raise
                
                # Exponential backoff
                import asyncio
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
        
        raise Exception("GitHub API: Max retries exceeded")
    
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
        
        # Retry with exponential backoff
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=headers, timeout=30.0)
                    
                    # Handle rate limiting (same as above)
                    if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
                        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                        if remaining == 0 and attempt < max_retries - 1:
                            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                            import time, asyncio
                            wait_time = max(reset_time - time.time(), retry_delay)
                            await asyncio.sleep(min(wait_time, 60))
                            continue
                    
                    response.raise_for_status()
                    return response.text
                    
            except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
                if attempt == max_retries - 1:
                    raise
                import asyncio
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
        
        raise Exception("GitHub API: Max retries exceeded")
    
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
        
        # Retry with exponential backoff
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        url,
                        headers=self.headers,
                        params=params,
                        timeout=30.0
                    )
                    
                    # Handle rate limiting
                    if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
                        remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                        if remaining == 0 and attempt < max_retries - 1:
                            reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                            import time, asyncio
                            wait_time = max(reset_time - time.time(), retry_delay)
                            await asyncio.sleep(min(wait_time, 60))
                            continue
                    
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    # Decode base64 content
                    import base64
                    content = base64.b64decode(data["content"]).decode("utf-8")
                    return content
                    
            except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
                if attempt == max_retries - 1:
                    raise
                import asyncio
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
        
        raise Exception("GitHub API: Max retries exceeded")
    
    def parse_repository(self, repository: str) -> tuple[str, str]:
        """
        Parse repository string into owner and repo name.
        
        Args:
            repository: Repository in format "owner/repo" or full GitHub URL
            
        Returns:
            Tuple of (owner, repo)
        """
        # Handle full GitHub URLs
        if repository.startswith(('http://', 'https://')):
            # Extract owner/repo from URL
            # https://github.com/owner/repo or https://github.com/owner/repo.git
            repository = repository.rstrip('/')
            if repository.endswith('.git'):
                repository = repository[:-4]
            parts = repository.split('/')
            if len(parts) >= 2:
                return parts[-2], parts[-1]
        
        # Handle owner/repo format
        parts = repository.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid repository format: {repository}. Expected 'owner/repo' or GitHub URL")
        return parts[0], parts[1]

# Made with Bob
