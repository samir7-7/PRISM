"""
Configuration management using Pydantic Settings.
Loads environment variables from .env file.
"""
from typing import List, Union
import json
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # GitHub Configuration
    github_token: str = ""
    github_api_url: str = "https://api.github.com"
    
    # IBM watsonx.ai Configuration
    ibm_bob_api_key: str = ""
    ibm_bob_api_url: str = "https://us-south.ml.cloud.ibm.com"
    ibm_bob_project_id: str = ""
    ibm_bob_model_id: str = "ibm/granite-13b-chat-v2"
    
    # Database Configuration
    database_url: str = "sqlite:///./prism.db"
    
    # Application Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    timeout: int = 60

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse JSON string list if provided."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [s.strip() for s in v.split(",")]
        return v


# Global settings instance
settings = Settings()

# Made with Bob
