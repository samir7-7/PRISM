"""CLI settings loaded from environment variables and ``.env``.

Resolution order (highest priority first): CLI flag → environment variable →
``.env`` in the working directory → built-in default. The CLI flag override is
handled in ``main.py`` by constructing ``Settings`` and then mutating the
relevant attribute before use.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from cli.errors import ConfigError


class Settings(BaseSettings):
    """PRISM CLI configuration.

    All fields are read from environment variables prefixed with ``PRISM_`` —
    e.g. ``PRISM_BACKEND_URL`` populates ``backend_url``. ``.env`` in the
    current working directory is loaded automatically.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PRISM_",
        case_sensitive=False,
        extra="ignore",
    )

    # Backend
    backend_url: str = "http://localhost:8000"
    timeout: int = 60

    # GitHub
    github_token: str | None = None
    repo_url: str | None = None

    # Output / UX
    output_format: Literal["pretty", "json"] = "pretty"
    auto_open: bool = False

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is within reasonable bounds."""
        if v < 1 or v > 300:
            raise ValueError("timeout must be between 1 and 300 seconds")
        return v

    def get_effective_repo_url(self, override: Optional[str] = None) -> str:
        """Get effective repository URL with optional override."""
        if override:
            return override
        if self.repo_url:
            return self.repo_url
        raise ConfigError(
            "Repository URL not configured",
            hint="pass --repo flag or set PRISM_REPO_URL in .env"
        )

    def get_effective_token(self, override: Optional[str] = None) -> Optional[str]:
        """Get effective GitHub token with optional override."""
        if override:
            return override
        return self.github_token

    def get_effective_backend_url(self, override: Optional[str] = None) -> str:
        """Get effective backend URL with optional override."""
        if override:
            return override
        return self.backend_url

    def validate_required_for_analysis(self, repo_url_override: Optional[str] = None) -> None:
        """Validate that required settings for analysis are present."""
        try:
            self.get_effective_repo_url(repo_url_override)
        except ConfigError:
            raise


def load_settings() -> Settings:
    """Load settings from environment and .env file."""
    return Settings()


# Alias for backward compatibility
ConfigurationError = ConfigError
