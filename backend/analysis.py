"""
Backend analysis module - Demo passthrough and heuristic scoring.

This module provides:
- Demo PR detection and canned responses
- Heuristic scoring from PR metadata
- Report ID generation
- GitHub PR file fetching with graceful degradation
"""
import hashlib
import httpx
from typing import Optional
from cli.demo_fixture import DEMO_PR_ID, DEMO_REPO_URL

# Canned response for demo PR
DEMO_RESPONSE = {
    "report_id": "demo8chr",
    "dashboard_url": "http://localhost:3000/report/demo8chr",
    "risk_score": 82,
    "risk_label": "HIGH",
    "impacted_node_count": 14,
    "status": "COMPLETE"
}


def is_demo(pr_id: str, repo_url: str) -> bool:
    """Check if the request matches the demo fixture."""
    return pr_id == DEMO_PR_ID and DEMO_REPO_URL in repo_url


def make_report_id(pr_id: str, repo_url: str) -> str:
    """Generate deterministic 8-character report ID from PR and repo."""
    combined = f"{pr_id}:{repo_url}"
    hash_digest = hashlib.sha1(combined.encode()).hexdigest()
    return hash_digest[:8]


def label_for(score: int) -> str:
    """Map risk score to 3-tier label (LOW/MEDIUM/HIGH)."""
    if score <= 40:
        return "LOW"
    elif score <= 70:
        return "MEDIUM"
    else:
        return "HIGH"


def score_from_files(files: list) -> int:
    """Calculate heuristic risk score from PR file metadata."""
    if not files:
        return 0
    
    # Simple heuristic: more files = higher risk
    base_score = min(len(files) * 10, 60)
    
    # Check for high-risk file patterns
    risk_boost = 0
    for file in files:
        filename = file.get("filename", "")
        if any(pattern in filename for pattern in ["auth", "payment", "security", "config"]):
            risk_boost += 10
        if filename.endswith((".sql", ".migration")):
            risk_boost += 5
    
    return min(base_score + risk_boost, 100)


def heuristic_from_pr_number(pr: str) -> tuple[int, int]:
    """Generate deterministic score and node count from PR number for testing."""
    try:
        pr_num = int(pr.replace("pr-", "").replace("#", ""))
        score = (pr_num * 7) % 100
        nodes = (pr_num * 3) % 20 + 1
        return score, nodes
    except (ValueError, AttributeError):
        return 50, 5


async def fetch_pr_files(
    owner: str,
    repo: str,
    pr_number: str,
    token: Optional[str] = None,
    client: Optional[httpx.AsyncClient] = None
) -> list:
    """
    Fetch PR file list from GitHub API.
    
    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: PR number (without 'pr-' prefix)
        token: Optional GitHub token
        client: Optional httpx client for testing
    
    Returns:
        List of file metadata dicts
    
    Raises:
        httpx.HTTPStatusError: On API errors
    """
    pr_num = pr_number.replace("pr-", "").replace("#", "")
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}/files"
    
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    
    if client is None:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    else:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()


async def analyze(
    pr_id: str,
    repo_url: str,
    http_client: Optional[httpx.AsyncClient] = None
) -> dict:
    """
    Top-level analysis function with demo detection and graceful degradation.
    
    This function:
    1. Checks if request is for demo PR (returns canned response)
    2. Attempts to fetch PR files from GitHub
    3. Calculates heuristic risk score
    4. Returns PARTIAL status on GitHub failures
    
    Args:
        pr_id: PR identifier (e.g., "pr-142")
        repo_url: Repository URL
        http_client: Optional httpx client for testing
    
    Returns:
        Dict with report_id, dashboard_url, risk_score, risk_label, 
        impacted_node_count, and status
    """
    # Demo passthrough
    if is_demo(pr_id, repo_url):
        return DEMO_RESPONSE
    
    # Generate report ID
    report_id = make_report_id(pr_id, repo_url)
    dashboard_url = f"http://localhost:3000/report/{report_id}"
    
    # Try to fetch PR files from GitHub
    try:
        # Parse owner/repo from URL
        if "github.com/" in repo_url:
            parts = repo_url.rstrip("/").split("github.com/")[-1].split("/")
            owner, repo = parts[0], parts[1]
        else:
            # Assume owner/repo format
            owner, repo = repo_url.split("/")[:2]
        
        files = await fetch_pr_files(owner, repo, pr_id, client=http_client)
        score = score_from_files(files)
        node_count = len(files)
        status = "COMPLETE"
        
    except Exception:
        # Graceful degradation: use heuristic from PR number
        score, node_count = heuristic_from_pr_number(pr_id)
        status = "PARTIAL"
    
    return {
        "report_id": report_id,
        "dashboard_url": dashboard_url,
        "risk_score": score,
        "risk_label": label_for(score),
        "impacted_node_count": node_count,
        "status": status
    }

# Made with Bob
