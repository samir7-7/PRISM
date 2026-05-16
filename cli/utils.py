"""
Utility functions for PRISM CLI.

This module provides validation, parsing, and helper functions used throughout
the CLI application.
"""

import re
import subprocess
from urllib.parse import urlparse

# ============================================================================
# PR Identifier Validation
# ============================================================================


def validate_pr_identifier(pr_id: str) -> bool:
    """
    Validate if a string is a valid PR identifier.

    Accepts formats:
    - Plain numbers: "123", "42"
    - Hash prefix: "#123", "#42"
    - PR prefix: "pr-123", "PR-42"
    - Pull prefix: "pull-123", "PULL-42"

    Args:
        pr_id: The PR identifier string to validate

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_pr_identifier("123")
        True
        >>> validate_pr_identifier("#123")
        True
        >>> validate_pr_identifier("pr-123")
        True
        >>> validate_pr_identifier("invalid")
        False
    """
    if not pr_id or not isinstance(pr_id, str):
        return False

    # Remove whitespace
    pr_id = pr_id.strip()

    # Pattern matches: 123, #123, pr-123, PR-123, pull-123, PULL-123
    pattern = r"^(?:#|pr-|PR-|pull-|PULL-)?(\d+)$"

    return bool(re.match(pattern, pr_id))


def normalize_pr_identifier(pr_id: str) -> str:
    """
    Normalize a PR identifier to a standard format (plain number).

    Converts various formats to a simple numeric string:
    - "#123" -> "123"
    - "pr-123" -> "123"
    - "PR-123" -> "123"
    - "pull-123" -> "123"
    - "123" -> "123"

    Args:
        pr_id: The PR identifier to normalize

    Returns:
        Normalized PR identifier (numeric string)

    Raises:
        ValueError: If the PR identifier is invalid

    Examples:
        >>> normalize_pr_identifier("#123")
        '123'
        >>> normalize_pr_identifier("pr-456")
        '456'
        >>> normalize_pr_identifier("789")
        '789'
    """
    if not validate_pr_identifier(pr_id):
        raise ValueError(
            f"Invalid PR identifier: '{pr_id}'. " f"Expected format: 123, #123, pr-123, or pull-123"
        )

    # Extract the numeric part
    pr_id = pr_id.strip()
    pattern = r"^(?:#|pr-|PR-|pull-|PULL-)?(\d+)$"
    match = re.match(pattern, pr_id)

    if match:
        return match.group(1)

    # This should never happen due to validation above, but just in case
    raise ValueError(f"Failed to normalize PR identifier: '{pr_id}'")


def extract_pr_number(pr_id: str) -> int:
    """
    Extract the numeric PR number from a PR identifier.

    Args:
        pr_id: The PR identifier

    Returns:
        The PR number as an integer

    Raises:
        ValueError: If the PR identifier is invalid

    Examples:
        >>> extract_pr_number("#123")
        123
        >>> extract_pr_number("pr-456")
        456
    """
    normalized = normalize_pr_identifier(pr_id)
    return int(normalized)


# ============================================================================
# Repository URL Validation
# ============================================================================


def validate_repository_url(url: str) -> bool:
    """
    Validate if a string is a valid GitHub or GitLab repository URL.

    Accepts formats:
    - HTTPS: https://github.com/owner/repo
    - HTTPS with .git: https://github.com/owner/repo.git
    - SSH: git@github.com:owner/repo.git
    - Short form: owner/repo

    Args:
        url: The repository URL to validate

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_repository_url("https://github.com/owner/repo")
        True
        >>> validate_repository_url("owner/repo")
        True
        >>> validate_repository_url("invalid")
        False
    """
    if not url or not isinstance(url, str):
        return False

    url = url.strip()

    # Pattern 1: Short form (owner/repo)
    short_pattern = r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$"
    if re.match(short_pattern, url):
        return True

    # Pattern 2: HTTPS URL
    https_pattern = r"^https?://(?:github\.com|gitlab\.com)/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+(\.git)?$"
    if re.match(https_pattern, url):
        return True

    # Pattern 3: SSH URL
    ssh_pattern = r"^git@(?:github\.com|gitlab\.com):[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+(\.git)?$"
    if re.match(ssh_pattern, url):
        return True

    return False


def parse_repository_url(url: str) -> dict:
    """
    Parse a repository URL and extract owner and repository name.

    Args:
        url: The repository URL to parse

    Returns:
        Dictionary with 'owner', 'repo', 'platform', and 'url' keys

    Raises:
        ValueError: If the URL is invalid

    Examples:
        >>> parse_repository_url("https://github.com/owner/repo")
        {'owner': 'owner', 'repo': 'repo', 'platform': 'github', 'url': 'https://github.com/owner/repo'}
        >>> parse_repository_url("owner/repo")
        {'owner': 'owner', 'repo': 'repo', 'platform': 'github', 'url': 'https://github.com/owner/repo'}
    """
    if not validate_repository_url(url):
        raise ValueError(
            f"Invalid repository URL: '{url}'. "
            f"Expected format: https://github.com/owner/repo or owner/repo"
        )

    url = url.strip()

    # Handle short form (owner/repo)
    short_pattern = r"^([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)$"
    match = re.match(short_pattern, url)
    if match:
        owner, repo = match.groups()
        repo = repo.rstrip(".git")
        return {
            "owner": owner,
            "repo": repo,
            "platform": "github",  # Default to GitHub for short form
            "url": f"https://github.com/{owner}/{repo}",
        }

    # Handle HTTPS URL
    https_pattern = (
        r"^https?://(github\.com|gitlab\.com)/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+?)(\.git)?$"
    )
    match = re.match(https_pattern, url)
    if match:
        platform_domain, owner, repo, _ = match.groups()
        platform = "github" if "github" in platform_domain else "gitlab"
        repo = repo.rstrip(".git")
        return {
            "owner": owner,
            "repo": repo,
            "platform": platform,
            "url": f"https://{platform_domain}/{owner}/{repo}",
        }

    # Handle SSH URL
    ssh_pattern = r"^git@(github\.com|gitlab\.com):([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+?)(\.git)?$"
    match = re.match(ssh_pattern, url)
    if match:
        platform_domain, owner, repo, _ = match.groups()
        platform = "github" if "github" in platform_domain else "gitlab"
        repo = repo.rstrip(".git")
        return {
            "owner": owner,
            "repo": repo,
            "platform": platform,
            "url": f"https://{platform_domain}/{owner}/{repo}",
        }

    # This should never happen due to validation above
    raise ValueError(f"Failed to parse repository URL: '{url}'")


def get_repository_display_name(url: str) -> str:
    """
    Get a human-readable display name for a repository.

    Args:
        url: The repository URL

    Returns:
        Display name in format "owner/repo"

    Examples:
        >>> get_repository_display_name("https://github.com/owner/repo")
        'owner/repo'
    """
    try:
        parsed = parse_repository_url(url)
        return f"{parsed['owner']}/{parsed['repo']}"
    except ValueError:
        # If parsing fails, return the original URL
        return url


# ============================================================================
# URL Utilities
# ============================================================================


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        url: The URL to validate

    Returns:
        True if valid, False otherwise

    Examples:
        >>> is_valid_url("http://localhost:8000")
        True
        >>> is_valid_url("https://api.example.com")
        True
        >>> is_valid_url("not a url")
        False
    """
    if not url or not isinstance(url, str):
        return False

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_backend_url(url: str) -> str:
    """
    Normalize a backend URL by removing trailing slashes and ensuring scheme.

    Args:
        url: The backend URL to normalize

    Returns:
        Normalized URL

    Examples:
        >>> normalize_backend_url("http://localhost:8000/")
        'http://localhost:8000'
        >>> normalize_backend_url("localhost:8000")
        'http://localhost:8000'
    """
    if not url:
        return url

    url = url.strip().rstrip("/")

    # Add http:// if no scheme is present
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"

    return url


# ============================================================================
# String Utilities
# ============================================================================


def truncate_text(text: str, max_length: int = 80, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, adding a suffix if truncated.

    Args:
        text: The text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add if truncated

    Returns:
        Truncated text

    Examples:
        >>> truncate_text("This is a very long text", 10)
        'This is...'
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: The filename to sanitize

    Returns:
        Sanitized filename

    Examples:
        >>> sanitize_filename("my/file:name.txt")
        'my_file_name.txt'
    """
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, "_", filename)


# ============================================================================
# Validation Helpers
# ============================================================================


def validate_positive_integer(value: str, name: str = "value") -> int:
    """
    Validate and convert a string to a positive integer.

    Args:
        value: The string value to validate
        name: Name of the value (for error messages)

    Returns:
        The validated integer

    Raises:
        ValueError: If the value is not a positive integer

    Examples:
        >>> validate_positive_integer("123", "timeout")
        123
    """
    try:
        int_value = int(value)
        if int_value <= 0:
            raise ValueError(f"{name} must be a positive integer, got: {value}")
        return int_value
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid {name}: '{value}'. Must be a positive integer.") from e


def validate_port(port: str) -> int:
    """
    Validate a port number.

    Args:
        port: The port number as a string

    Returns:
        The validated port number

    Raises:
        ValueError: If the port is invalid

    Examples:
        >>> validate_port("8000")
        8000
    """
    try:
        port_num = int(port)
        if not (1 <= port_num <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, got: {port}")
        return port_num
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid port: '{port}'") from e


# ============================================================================
# Git Remote Detection
# ============================================================================


def detect_git_remote(cwd: str | None = None) -> str | None:
    """Return the normalized URL of ``origin`` for the git repo at ``cwd``.

    Shells out to ``git remote get-url origin`` with a tight 2-second timeout,
    then runs the result through :func:`parse_repository_url` so SSH and short
    forms are converted to the canonical ``https://host/owner/repo`` shape the
    backend expects.

    Returns ``None`` on every failure path — no git binary, not inside a repo,
    no ``origin`` remote, unparseable URL, timeout. Never raises; the caller
    is expected to fall back to ``--repo`` / ``PRISM_REPO_URL``.

    Args:
        cwd: Directory to run ``git`` from. Defaults to the process cwd.
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=2.0,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None

    if result.returncode != 0:
        return None

    raw = (result.stdout or "").strip()
    if not raw:
        return None

    try:
        return parse_repository_url(raw)["url"]
    except ValueError:
        return None


# Made with Bob
