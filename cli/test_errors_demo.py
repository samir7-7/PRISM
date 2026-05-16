"""
Demo script to test the custom error handling system.

This script demonstrates various error scenarios and how they are
formatted and displayed to the user.
"""

from errors import (
    InvalidPRIdentifierError,
    InvalidRepositoryURLError,
    InvalidPortError,
    BackendUnreachableError,
    BackendValidationError,
    BackendServerError,
    MissingTokenError,
)
from formatter import format_error, format_success, format_info, format_warning
from utils import (
    normalize_pr_identifier,
    parse_repository_url,
    validate_port,
    validate_positive_integer,
)


def test_validation_errors():
    """Test validation error formatting."""
    print("\n" + "="*60)
    print("TESTING VALIDATION ERRORS")
    print("="*60)
    
    # Test 1: Invalid PR identifier
    print("\n1. Invalid PR Identifier:")
    try:
        normalize_pr_identifier("invalid-pr")
    except Exception as e:
        format_error(e)
    
    # Test 2: Invalid repository URL
    print("\n2. Invalid Repository URL:")
    try:
        parse_repository_url("not-a-valid-url")
    except Exception as e:
        format_error(e)
    
    # Test 3: Invalid port
    print("\n3. Invalid Port:")
    try:
        validate_port("99999")
    except Exception as e:
        format_error(e)
    
    # Test 4: Invalid positive integer
    print("\n4. Invalid Positive Integer:")
    try:
        validate_positive_integer("-5", "timeout")
    except Exception as e:
        format_error(e)


def test_network_errors():
    """Test network error formatting."""
    print("\n" + "="*60)
    print("TESTING NETWORK ERRORS")
    print("="*60)
    
    # Test 1: Backend unreachable
    print("\n1. Backend Unreachable:")
    try:
        raise BackendUnreachableError(
            "http://localhost:8000",
            reason="Connection refused"
        )
    except Exception as e:
        format_error(e)


def test_api_errors():
    """Test API error formatting."""
    print("\n" + "="*60)
    print("TESTING API ERRORS")
    print("="*60)
    
    # Test 1: Backend validation error
    print("\n1. Backend Validation Error:")
    try:
        raise BackendValidationError(
            "PR identifier must be a positive integer",
            field="pr_identifier"
        )
    except Exception as e:
        format_error(e)
    
    # Test 2: Backend server error
    print("\n2. Backend Server Error:")
    try:
        raise BackendServerError("Internal server error during analysis")
    except Exception as e:
        format_error(e)


def test_config_errors():
    """Test configuration error formatting."""
    print("\n" + "="*60)
    print("TESTING CONFIGURATION ERRORS")
    print("="*60)
    
    # Test 1: Missing token
    print("\n1. Missing GitHub Token:")
    try:
        raise MissingTokenError("private repository access")
    except Exception as e:
        format_error(e)


def test_success_scenarios():
    """Test successful operations."""
    print("\n" + "="*60)
    print("TESTING SUCCESS SCENARIOS")
    print("="*60)
    
    # Test 1: Valid PR identifier
    print("\n1. Valid PR Identifier:")
    try:
        result = normalize_pr_identifier("#123")
        format_success(f"Successfully normalized PR identifier to: {result}")
    except Exception as e:
        format_error(e)
    
    # Test 2: Valid repository URL
    print("\n2. Valid Repository URL:")
    try:
        result = parse_repository_url("owner/repo")
        format_success(f"Successfully parsed repository: {result['owner']}/{result['repo']}")
    except Exception as e:
        format_error(e)
    
    # Test 3: Valid port
    print("\n3. Valid Port:")
    try:
        result = validate_port("8000")
        format_success(f"Valid port number: {result}")
    except Exception as e:
        format_error(e)


def test_other_formatting():
    """Test other formatting utilities."""
    print("\n" + "="*60)
    print("TESTING OTHER FORMATTING")
    print("="*60)
    
    print("\n1. Info Message:")
    format_info("This is an informational message", title="Information")
    
    print("\n2. Warning Message:")
    format_warning("This is a warning message")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("PRISM CLI - ERROR HANDLING DEMO")
    print("="*60)
    
    test_validation_errors()
    test_network_errors()
    test_api_errors()
    test_config_errors()
    test_success_scenarios()
    test_other_formatting()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

# Made with Bob
