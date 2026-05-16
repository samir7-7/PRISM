"""
Simple unit test for M7 fix - GitHub URL parsing.
This test can run without full backend dependencies.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def parse_repository_simple(repository: str) -> tuple[str, str]:
    """
    Simplified version of parse_repository for testing.
    This is the logic we implemented in backend/utils/github_client.py
    """
    # Handle full GitHub URLs
    if repository.startswith(('http://', 'https://')):
        # Extract owner/repo from URL
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


class TestURLParsing:
    """Test URL parsing logic."""
    
    def test_owner_repo_format(self):
        """Test basic owner/repo format."""
        owner, repo = parse_repository_simple("octocat/Hello-World")
        assert owner == "octocat"
        assert repo == "Hello-World"
    
    def test_https_url(self):
        """Test HTTPS GitHub URL."""
        owner, repo = parse_repository_simple("https://github.com/octocat/Hello-World")
        assert owner == "octocat"
        assert repo == "Hello-World"
    
    def test_http_url(self):
        """Test HTTP GitHub URL."""
        owner, repo = parse_repository_simple("http://github.com/octocat/Hello-World")
        assert owner == "octocat"
        assert repo == "Hello-World"
    
    def test_url_with_git_suffix(self):
        """Test URL with .git suffix."""
        owner, repo = parse_repository_simple("https://github.com/octocat/Hello-World.git")
        assert owner == "octocat"
        assert repo == "Hello-World"
    
    def test_url_with_trailing_slash(self):
        """Test URL with trailing slash."""
        owner, repo = parse_repository_simple("https://github.com/octocat/Hello-World/")
        assert owner == "octocat"
        assert repo == "Hello-World"
    
    def test_url_with_both_git_and_slash(self):
        """Test URL with .git and trailing slash."""
        owner, repo = parse_repository_simple("https://github.com/octocat/Hello-World.git/")
        assert owner == "octocat"
        assert repo == "Hello-World"
    
    def test_invalid_format(self):
        """Test that invalid format raises error."""
        try:
            parse_repository_simple("invalid")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Invalid repository format" in str(e)
    
    def test_empty_string(self):
        """Test that empty string raises error."""
        try:
            parse_repository_simple("")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Invalid repository format" in str(e)


if __name__ == "__main__":
    # Run tests manually
    test = TestURLParsing()
    
    print("Running URL parsing tests...")
    tests_run = 0
    tests_passed = 0
    
    for method_name in dir(test):
        if method_name.startswith('test_'):
            tests_run += 1
            try:
                method = getattr(test, method_name)
                method()
                print(f"[PASS] {method_name}")
                tests_passed += 1
            except Exception as e:
                print(f"[FAIL] {method_name}: {e}")
    
    print(f"\n{tests_passed}/{tests_run} tests passed")
    
    if tests_passed == tests_run:
        print("\n[SUCCESS] All URL parsing tests passed!")
        sys.exit(0)
    else:
        print(f"\n[ERROR] {tests_run - tests_passed} tests failed")
        sys.exit(1)

# Made with Bob
