"""
Custom exceptions for PRISM CLI.

This module defines a hierarchy of exceptions used throughout the CLI application
to provide clear, user-friendly error messages with error codes and suggestions.

Error Code Ranges:
- E1xxx: Validation errors (invalid input, format issues)
- E2xxx: Network errors (connection, timeout, unreachable)
- E3xxx: API errors (backend responses, authentication)
- E4xxx: Configuration errors (missing config, invalid settings)
"""

from typing import Optional


# ============================================================================
# Base Exception
# ============================================================================

class PRISMError(Exception):
    """
    Base exception for all PRISM CLI errors.
    
    All custom exceptions inherit from this class, allowing for easy
    catching of all PRISM-specific errors.
    
    Attributes:
        code: Unique error code (e.g., "E1001")
        message: Human-readable error message
        suggestion: Optional suggestion for fixing the error
        details: Optional additional context
    """
    
    def __init__(
        self,
        message: str,
        code: str = "E0000",
        suggestion: Optional[str] = None,
        details: Optional[dict] = None
    ):
        self.code = code
        self.message = message
        self.suggestion = suggestion
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Return formatted error message."""
        parts = [f"[{self.code}] {self.message}"]
        if self.suggestion:
            parts.append(f"\n💡 Suggestion: {self.suggestion}")
        return "".join(parts)


# ============================================================================
# Validation Errors (E1xxx)
# ============================================================================

class ValidationError(PRISMError):
    """Base class for validation errors."""
    
    def __init__(self, message: str, code: str = "E1000", **kwargs):
        super().__init__(message, code, **kwargs)


class InvalidPRIdentifierError(ValidationError):
    """Raised when a PR identifier is invalid."""
    
    def __init__(self, pr_id: str, suggestion: Optional[str] = None):
        message = (
            f"Invalid PR identifier: '{pr_id}'\n\n"
            f"Expected format:\n"
            f"  • Plain number: 123\n"
            f"  • Hash prefix: #123\n"
            f"  • PR prefix: pr-123 or PR-123\n"
            f"  • Pull prefix: pull-123 or PULL-123"
        )
        super().__init__(
            message=message,
            code="E1001",
            suggestion=suggestion or "Use a valid PR number like '123' or '#123'",
            details={"pr_id": pr_id}
        )


class InvalidRepositoryURLError(ValidationError):
    """Raised when a repository URL is invalid."""
    
    def __init__(self, url: str, suggestion: Optional[str] = None):
        message = (
            f"Invalid repository URL: '{url}'\n\n"
            f"Expected format:\n"
            f"  • HTTPS: https://github.com/owner/repo\n"
            f"  • HTTPS with .git: https://github.com/owner/repo.git\n"
            f"  • SSH: git@github.com:owner/repo.git\n"
            f"  • Short form: owner/repo"
        )
        super().__init__(
            message=message,
            code="E1002",
            suggestion=suggestion or "Use format: owner/repo or https://github.com/owner/repo",
            details={"url": url}
        )


class InvalidPortError(ValidationError):
    """Raised when a port number is invalid."""
    
    def __init__(self, port: str, suggestion: Optional[str] = None):
        message = f"Invalid port number: '{port}'"
        super().__init__(
            message=message,
            code="E1003",
            suggestion=suggestion or "Port must be between 1 and 65535",
            details={"port": port}
        )


class InvalidPositiveIntegerError(ValidationError):
    """Raised when a value must be a positive integer but isn't."""
    
    def __init__(self, value: str, name: str = "value", suggestion: Optional[str] = None):
        message = f"Invalid {name}: '{value}' (must be a positive integer)"
        super().__init__(
            message=message,
            code="E1004",
            suggestion=suggestion or f"Provide a positive integer for {name}",
            details={"value": value, "name": name}
        )


# ============================================================================
# Network Errors (E2xxx)
# ============================================================================

class NetworkError(PRISMError):
    """Base class for network-related errors."""
    
    def __init__(self, message: str, code: str = "E2000", **kwargs):
        super().__init__(message, code, **kwargs)


class BackendUnreachableError(NetworkError):
    """Raised when the backend server cannot be reached."""
    
    def __init__(self, backend_url: str, reason: Optional[str] = None):
        message = f"Cannot reach backend server at: {backend_url}"
        if reason:
            message += f"\nReason: {reason}"
        
        super().__init__(
            message=message,
            code="E2001",
            suggestion="Check that the backend URL is correct and the server is running",
            details={"backend_url": backend_url, "reason": reason}
        )


class ConnectionTimeoutError(NetworkError):
    """Raised when a connection times out."""
    
    def __init__(self, backend_url: str, timeout: int):
        message = f"Connection to {backend_url} timed out after {timeout} seconds"
        super().__init__(
            message=message,
            code="E2002",
            suggestion="Try again or increase the timeout value",
            details={"backend_url": backend_url, "timeout": timeout}
        )


class RequestFailedError(NetworkError):
    """Raised when an HTTP request fails."""
    
    def __init__(self, url: str, status_code: int, reason: Optional[str] = None):
        message = f"Request to {url} failed with status {status_code}"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message=message,
            code="E2003",
            suggestion="Check the server logs or try again later",
            details={"url": url, "status_code": status_code, "reason": reason}
        )


# ============================================================================
# API Errors (E3xxx)
# ============================================================================

class APIError(PRISMError):
    """Base class for API-related errors."""
    
    def __init__(self, message: str, code: str = "E3000", **kwargs):
        super().__init__(message, code, **kwargs)


class BackendValidationError(APIError):
    """Raised when the backend returns a 422 validation error."""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        message = "Backend validation failed"
        if field:
            message += f" for field '{field}'"
        message += f": {detail}"
        
        super().__init__(
            message=message,
            code="E3001",
            suggestion="Check your input parameters and try again",
            details={"detail": detail, "field": field}
        )


class BackendServerError(APIError):
    """Raised when the backend returns a 500 server error."""
    
    def __init__(self, detail: Optional[str] = None):
        message = "Backend server error"
        if detail:
            message += f": {detail}"
        
        super().__init__(
            message=message,
            code="E3002",
            suggestion="This is a server-side issue. Try again later or contact support",
            details={"detail": detail}
        )


class UnauthorizedError(APIError):
    """Raised when authentication fails (401)."""
    
    def __init__(self, detail: Optional[str] = None):
        message = "Authentication failed"
        if detail:
            message += f": {detail}"
        
        super().__init__(
            message=message,
            code="E3003",
            suggestion="Check your GitHub token or provide a valid token with --token",
            details={"detail": detail}
        )


class BackendHealthCheckFailedError(APIError):
    """Raised when the backend health check fails."""
    
    def __init__(self, backend_url: str, reason: Optional[str] = None):
        message = f"Backend health check failed for {backend_url}"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message=message,
            code="E3004",
            suggestion="The backend may be starting up or experiencing issues",
            details={"backend_url": backend_url, "reason": reason}
        )


# ============================================================================
# Configuration Errors (E4xxx)
# ============================================================================

class ConfigError(PRISMError):
    """Base class for configuration errors."""
    
    def __init__(self, message: str, code: str = "E4000", **kwargs):
        super().__init__(message, code, **kwargs)


class MissingTokenError(ConfigError):
    """Raised when a GitHub token is required but not provided."""
    
    def __init__(self, context: Optional[str] = None):
        message = "GitHub token is required"
        if context:
            message += f" for {context}"
        
        super().__init__(
            message=message,
            code="E4001",
            suggestion=(
                "Provide a token using:\n"
                "  • --token flag\n"
                "  • GITHUB_TOKEN environment variable\n"
                "  • .env file"
            ),
            details={"context": context}
        )


class InvalidBackendURLError(ConfigError):
    """Raised when the backend URL is invalid."""
    
    def __init__(self, url: str):
        message = f"Invalid backend URL: '{url}'"
        super().__init__(
            message=message,
            code="E4002",
            suggestion="Provide a valid URL like http://localhost:8000 or https://api.example.com",
            details={"url": url}
        )


class MissingConfigError(ConfigError):
    """Raised when required configuration is missing."""
    
    def __init__(self, config_name: str, suggestion: Optional[str] = None):
        message = f"Missing required configuration: {config_name}"
        super().__init__(
            message=message,
            code="E4003",
            suggestion=suggestion or f"Provide {config_name} in your configuration",
            details={"config_name": config_name}
        )


# ============================================================================
# Helper Functions
# ============================================================================

def format_error_for_display(error: PRISMError) -> dict:
    """
    Format a PRISMError for display in the CLI.
    
    Returns a dictionary with structured error information that can be
    used by the formatter module to create rich console output.
    
    Args:
        error: The PRISMError to format
        
    Returns:
        Dictionary with error information
    """
    return {
        "code": error.code,
        "message": error.message,
        "suggestion": error.suggestion,
        "details": error.details
    }


def is_prism_error(error: Exception) -> bool:
    """
    Check if an exception is a PRISM error.
    
    Args:
        error: The exception to check
        
    Returns:
        True if the error is a PRISMError, False otherwise
    """
    return isinstance(error, PRISMError)

# Made with Bob