"""CLI settings loaded from environment variables and ``.env``.

Resolution order (highest priority first): CLI flag → environment variable →
``.env`` in the working directory → built-in default. The CLI flag override is
handled in ``main.py`` by constructing ``Settings`` and then mutating the
relevant attribute before use.
"""

from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


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
