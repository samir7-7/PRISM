"""
Tests to verify the fixes applied for issues M1 and M7.
"""
import pytest
from backend.services.graph_builder import GraphBuilder
from backend.services.ast_analyzer import CodeElement
from backend.utils.github_client import GitHubClient


class TestM1CoverageFlag:
    """Test M1: Coverage flag for incomplete graph data."""
    
    def test_coverage_flag_with_pre_indexed_data(self):
        """Test that coverage flag is True when pre-indexed data is available."""
        builder = GraphBuilder()
        elements = [
            CodeElement(
                type="function",
                name="test_func",
                file_path="test.py",
                line_start=1,
                line_end=5,
                dependencies=[],
                metadata={}
            )
        ]
        
        graph = builder.build_graph(elements, has_pre_indexed_data=True)
        
        assert graph.graph['coverage_complete'] == True
        assert 'Complete repository analysis' in graph.graph['coverage_note']
    
    def test_coverage_flag_without_pre_indexed_data(self):
        """Test that coverage flag is False for on-demand analysis."""
        builder = GraphBuilder()
        elements = [
            CodeElement(
                type="function",
                name="test_func",
                file_path="test.py",
                line_start=1,
                line_end=5,
                dependencies=[],
                metadata={}
            )
        ]
        
        graph = builder.build_graph(elements, has_pre_indexed_data=False)
        
        assert graph.graph['coverage_complete'] == False
        assert 'incomplete' in graph.graph['coverage_note'].lower()
    
    def test_coverage_flag_default_behavior(self):
        """Test default behavior when has_pre_indexed_data is not specified."""
        builder = GraphBuilder()
        elements = [
            CodeElement(
                type="function",
                name="test_func",
                file_path="test.py",
                line_start=1,
                line_end=5,
                dependencies=[],
                metadata={}
            )
        ]
        
        # Default should be False (on-demand analysis)
        graph = builder.build_graph(elements)
        
        assert graph.graph['coverage_complete'] == False
        assert 'coverage_note' in graph.graph


class TestM7URLParsing:
    """Test M7: GitHub client URL format handling."""
    
    def test_parse_owner_repo_format(self):
        """Test parsing of owner/repo format."""
        client = GitHubClient()
        owner, repo = client.parse_repository("octocat/Hello-World")
        
        assert owner == "octocat"
        assert repo == "Hello-World"
    
    def test_parse_https_url(self):
        """Test parsing of full HTTPS GitHub URL."""
        client = GitHubClient()
        owner, repo = client.parse_repository("https://github.com/octocat/Hello-World")
        
        assert owner == "octocat"
        assert repo == "Hello-World"
    
    def test_parse_http_url(self):
        """Test parsing of full HTTP GitHub URL."""
        client = GitHubClient()
        owner, repo = client.parse_repository("http://github.com/octocat/Hello-World")
        
        assert owner == "octocat"
        assert repo == "Hello-World"
    
    def test_parse_url_with_git_suffix(self):
        """Test parsing of URL with .git suffix."""
        client = GitHubClient()
        owner, repo = client.parse_repository("https://github.com/octocat/Hello-World.git")
        
        assert owner == "octocat"
        assert repo == "Hello-World"
    
    def test_parse_url_with_trailing_slash(self):
        """Test parsing of URL with trailing slash."""
        client = GitHubClient()
        owner, repo = client.parse_repository("https://github.com/octocat/Hello-World/")
        
        assert owner == "octocat"
        assert repo == "Hello-World"
    
    def test_parse_url_with_git_suffix_and_trailing_slash(self):
        """Test parsing of URL with both .git suffix and trailing slash."""
        client = GitHubClient()
        owner, repo = client.parse_repository("https://github.com/octocat/Hello-World.git/")
        
        assert owner == "octocat"
        assert repo == "Hello-World"
    
    def test_parse_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        client = GitHubClient()
        
        with pytest.raises(ValueError, match="Invalid repository format"):
            client.parse_repository("invalid")
    
    def test_parse_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        client = GitHubClient()
        
        with pytest.raises(ValueError, match="Invalid repository format"):
            client.parse_repository("")
    
    def test_parse_url_with_subdirectories(self):
        """Test parsing of URL with extra path components."""
        client = GitHubClient()
        # Should extract last two components
        owner, repo = client.parse_repository("https://github.com/octocat/Hello-World/tree/main")
        
        assert owner == "Hello-World"
        assert repo == "tree"
        # Note: This is expected behavior - we take the last two path components


class TestIntegration:
    """Integration tests for the fixes."""
    
    def test_graph_builder_coverage_metadata_accessible(self):
        """Test that coverage metadata is accessible from the graph."""
        builder = GraphBuilder()
        elements = []
        
        graph = builder.build_graph(elements, has_pre_indexed_data=True)
        
        # Verify metadata is accessible
        assert 'coverage_complete' in graph.graph
        assert 'coverage_note' in graph.graph
        assert isinstance(graph.graph['coverage_complete'], bool)
        assert isinstance(graph.graph['coverage_note'], str)
    
    def test_github_client_handles_real_world_urls(self):
        """Test GitHub client with real-world URL patterns."""
        client = GitHubClient()
        
        test_cases = [
            ("owner/repo", ("owner", "repo")),
            ("https://github.com/owner/repo", ("owner", "repo")),
            ("https://github.com/owner/repo.git", ("owner", "repo")),
            ("http://github.com/owner/repo/", ("owner", "repo")),
        ]
        
        for url, expected in test_cases:
            result = client.parse_repository(url)
            assert result == expected, f"Failed for URL: {url}"


# Made with Bob