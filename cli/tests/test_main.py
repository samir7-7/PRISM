"""
Tests for cli/main.py

Tests CLI commands using Typer's CliRunner.
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from cli.main import app
from cli import __version__


runner = CliRunner()


def test_help_command():
    """Test --help flag shows usage information."""
    result = runner.invoke(app, ["--help"])
    
    assert result.exit_code == 0
    assert "PRISM" in result.stdout
    assert "Pull Request Intelligent Semantic Monitor" in result.stdout
    assert "analyze" in result.stdout
    assert "demo" in result.stdout
    assert "version" in result.stdout


def test_version_command():
    """Test version command shows version number."""
    result = runner.invoke(app, ["version"])
    
    assert result.exit_code == 0
    assert __version__ in result.stdout
    assert "PRISM CLI" in result.stdout


def test_analyze_help():
    """Test analyze command help."""
    result = runner.invoke(app, ["analyze", "--help"])
    
    assert result.exit_code == 0
    assert "Analyze a pull request" in result.stdout
    assert "--repo" in result.stdout
    assert "--backend" in result.stdout
    assert "--token" in result.stdout
    assert "--open" in result.stdout
    # --json is hidden from help output (hidden=True in main.py:68)
    assert "--json" not in result.stdout


def test_analyze_missing_repo_url():
    """Test analyze command fails when no repository URL is provided."""
    result = runner.invoke(app, ["analyze", "pr-142"])
    
    assert result.exit_code == 1
    assert "No repository URL" in result.stdout or "repository" in result.stdout.lower()


def test_analyze_with_repo_backend_down():
    """Test analyze command when backend is unreachable."""
    with patch("cli.main.AnalysisClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.check_health.return_value = False
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client
        
        result = runner.invoke(app, [
            "analyze", "pr-142",
            "--repo", "https://github.com/test/repo"
        ])
        
        assert result.exit_code == 1
        assert "Cannot reach" in result.stdout or "backend" in result.stdout.lower()


def test_analyze_success_pretty_output(mock_analysis_response):
    """Test successful analysis with pretty output."""
    with patch("cli.main.AnalysisClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client.run.return_value = mock_analysis_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client
        
        result = runner.invoke(app, [
            "analyze", "pr-142",
            "--repo", "https://github.com/test/repo"
        ])
        
        assert result.exit_code == 0
        # Check for key output elements
        assert "PRISM" in result.stdout or "analysis" in result.stdout.lower()


def test_analyze_success_json_output(mock_analysis_response):
    """Test successful analysis with JSON output."""
    with patch("cli.main.AnalysisClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client.run.return_value = mock_analysis_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client
        
        result = runner.invoke(app, [
            "analyze", "pr-142",
            "--repo", "https://github.com/test/repo",
            "--json"
        ])
        
        assert result.exit_code == 0
        # Should contain JSON output
        assert "report_id" in result.stdout or "{" in result.stdout


def test_analyze_with_all_flags():
    """Test analyze command with all flags provided."""
    with patch("cli.main.AnalysisClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client.run.return_value = MagicMock(
            report_id="test",
            dashboard_url="http://test",
            risk_score=50,
            risk_label="MEDIUM",
            impacted_node_count=5,
            status="COMPLETE",
            model_dump=lambda: {}
        )
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client
        
        with patch("cli.main.webbrowser.open") as mock_browser:
            result = runner.invoke(app, [
                "analyze", "pr-142",
                "--repo", "https://github.com/test/repo",
                "--backend", "http://custom:8000",
                "--token", "ghp_test",
                "--open"
            ])
            
            assert result.exit_code == 0
            # Verify browser was opened
            mock_browser.assert_called_once()


def test_demo_command():
    """Test demo command."""
    with patch("cli.main.AnalysisClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client.run.return_value = MagicMock(
            report_id="demo",
            dashboard_url="http://test",
            risk_score=75,
            risk_label="HIGH",
            impacted_node_count=10,
            status="COMPLETE",
            model_dump=lambda: {}
        )
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client
        
        with patch("cli.main.webbrowser.open"):
            result = runner.invoke(app, ["demo"])
            
            # Demo should succeed (uses hardcoded values)
            assert result.exit_code == 0
            assert "demo" in result.stdout.lower() or "pr-142" in result.stdout.lower()


def test_demo_with_custom_backend():
    """Test demo command with custom backend."""
    with patch("cli.main.AnalysisClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client.run.return_value = MagicMock(
            report_id="demo",
            dashboard_url="http://test",
            risk_score=75,
            risk_label="HIGH",
            impacted_node_count=10,
            status="COMPLETE",
            model_dump=lambda: {}
        )
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client
        
        with patch("cli.main.webbrowser.open"):
            result = runner.invoke(app, ["demo", "--backend", "http://custom:9000"])
            
            assert result.exit_code == 0


def test_keyboard_interrupt_handling():
    """Test graceful handling of Ctrl+C."""
    with patch("cli.main.AnalysisClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client.run.side_effect = KeyboardInterrupt()
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client
        
        result = runner.invoke(app, [
            "analyze", "pr-142",
            "--repo", "https://github.com/test/repo"
        ])
        
        assert result.exit_code == 130  # Standard exit code for SIGINT
        assert "cancelled" in result.stdout.lower() or "interrupt" in result.stdout.lower()

# Made with Bob
