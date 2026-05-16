"""
Tests for cli/config.py

Tests configuration loading, validation, and override behavior.
"""

import pytest
import os
from unittest.mock import patch

from cli.config import Settings, load_settings
from cli.errors import ConfigurationError


def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    
    assert settings.backend_url == "http://localhost:8000"
    assert settings.github_token is None
    assert settings.repo_url is None
    assert settings.timeout == 60
    assert settings.output_format == "pretty"
    assert settings.auto_open is False


def test_settings_with_env_vars():
    """Test settings loaded from environment variables."""
    with patch.dict(os.environ, {
        "PRISM_BACKEND_URL": "http://test-backend:9000",
        "PRISM_GITHUB_TOKEN": "ghp_test_token",
        "PRISM_REPO_URL": "https://github.com/test/repo",
        "PRISM_TIMEOUT": "120",
        "PRISM_OUTPUT_FORMAT": "json",
        "PRISM_AUTO_OPEN": "true"
    }):
        settings = Settings()
        
        assert settings.backend_url == "http://test-backend:9000"
        assert settings.github_token == "ghp_test_token"
        assert settings.repo_url == "https://github.com/test/repo"
        assert settings.timeout == 120
        assert settings.output_format == "json"
        assert settings.auto_open is True


def test_settings_timeout_validation():
    """Test timeout validation (must be between 1 and 300)."""
    # Valid timeout
    settings = Settings(timeout=30)
    assert settings.timeout == 30
    
    # Invalid timeout (too low)
    with pytest.raises(Exception):  # Pydantic validation error
        Settings(timeout=0)
    
    # Invalid timeout (too high)
    with pytest.raises(Exception):  # Pydantic validation error
        Settings(timeout=500)


def test_settings_output_format_validation():
    """Test output_format validation (must be 'pretty' or 'json')."""
    # Valid formats
    settings = Settings(output_format="pretty")
    assert settings.output_format == "pretty"
    
    settings = Settings(output_format="json")
    assert settings.output_format == "json"
    
    # Invalid format
    with pytest.raises(Exception):  # Pydantic validation error
        Settings(output_format="xml")


def test_get_effective_repo_url():
    """Test getting effective repository URL with override."""
    settings = Settings(repo_url="https://github.com/default/repo")
    
    # Use default
    assert settings.get_effective_repo_url() == "https://github.com/default/repo"
    
    # Use override
    override = "https://github.com/override/repo"
    assert settings.get_effective_repo_url(override) == override


def test_get_effective_repo_url_missing():
    """Test error when no repository URL is available."""
    settings = Settings()  # No repo_url set
    
    with pytest.raises(ConfigurationError) as exc_info:
        settings.get_effective_repo_url()
    
    assert "repository_url" in str(exc_info.value).lower()


def test_get_effective_token():
    """Test getting effective GitHub token with override."""
    settings = Settings(github_token="default_token")
    
    # Use default
    assert settings.get_effective_token() == "default_token"
    
    # Use override
    assert settings.get_effective_token("override_token") == "override_token"
    
    # No token
    settings = Settings()
    assert settings.get_effective_token() is None


def test_get_effective_backend_url():
    """Test getting effective backend URL with override."""
    settings = Settings(backend_url="http://default:8000")
    
    # Use default
    assert settings.get_effective_backend_url() == "http://default:8000"
    
    # Use override
    assert settings.get_effective_backend_url("http://override:9000") == "http://override:9000"


def test_validate_required_for_analysis():
    """Test validation of required settings for analysis."""
    # Valid: repo_url set
    settings = Settings(repo_url="https://github.com/test/repo")
    settings.validate_required_for_analysis()  # Should not raise
    
    # Valid: override provided
    settings = Settings()
    settings.validate_required_for_analysis(repo_url_override="https://github.com/test/repo")
    
    # Invalid: no repo_url
    settings = Settings()
    with pytest.raises(ConfigurationError) as exc_info:
        settings.validate_required_for_analysis()
    
    assert "repository_url" in str(exc_info.value).lower()


def test_load_settings():
    """Test load_settings helper function."""
    settings = load_settings()
    assert isinstance(settings, Settings)
    assert settings.backend_url == "http://localhost:8000"


def test_settings_case_insensitive():
    """Test that environment variable names are case-insensitive."""
    with patch.dict(os.environ, {
        "prism_backend_url": "http://test:8000",  # lowercase
        "PRISM_GITHUB_TOKEN": "token123",  # uppercase
    }):
        settings = Settings()
        
        # Both should work due to case_sensitive=False
        assert settings.backend_url == "http://test:8000"
        assert settings.github_token == "token123"


def test_settings_extra_fields_ignored():
    """Test that extra fields in environment are ignored."""
    with patch.dict(os.environ, {
        "PRISM_BACKEND_URL": "http://test:8000",
        "PRISM_UNKNOWN_FIELD": "should_be_ignored",
    }):
        settings = Settings()
        
        # Should not raise error, extra field is ignored
        assert settings.backend_url == "http://test:8000"
        assert not hasattr(settings, "unknown_field")

# Made with Bob
